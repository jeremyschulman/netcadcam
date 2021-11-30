# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import json
from typing import Tuple, List, Dict
from pathlib import Path

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import click
from rich.table import Table
from rich.console import Console
from rich.pretty import Pretty


# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.config import Environment, netcad_globals
from netcad.logger import get_logger

from netcad.cli.common_opts import opt_devices, opt_designs
from netcad.cli.device_inventory import get_devices_from_designs

from netcad.netcam import tc_result_types as trt
from netcad.cli.netcam.cli_netcam_main import cli

# -----------------------------------------------------------------------------
# Exports (none)
# -----------------------------------------------------------------------------

__all__ = []


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@cli.command(name="report")
@opt_devices()
@opt_designs(required=True)
@click.option(
    "--tests-dir",
    help="location to read test-cases",
    type=click.Path(path_type=Path, resolve_path=True, exists=True, writable=True),
    envvar=Environment.NETCAD_TESTCASESDIR,
)
@click.option(
    "-ef",
    "--exclude-field",
    "exclude_fields",
    multiple=True,
    help="exclude field from report",
)
@click.option(
    "-if",
    "--include-field",
    "include_fields",
    multiple=True,
    help="include only field from report",
)
@click.option(
    "--tests",
    "testing_service_names",
    multiple=True,
    help="display only logs from <test>",
)
@click.option(
    "--all", "include_all", is_flag=True, help="display all results, not just FAIL"
)
def cli_report_tests(devices: Tuple[str], designs: Tuple[str], **optionals):
    """Show test results in tablular form."""

    log = get_logger()

    if not (device_objs := get_devices_from_designs(designs, include_devices=devices)):
        log.error("No devices located in the given designs")
        return

    log.info(f"Showing test logs for {len(device_objs)} devices.")

    for dev_obj in device_objs:
        show_device_test_logs(dev_obj, optionals)


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def show_device_test_logs(device: Device, optionals: dict):

    log = get_logger()

    dev_tcr_dir = netcad_globals.g_netcad_testcases_dir / device.name / "results"
    if not dev_tcr_dir.exists():
        log.error(
            f"Missing {device.name}, expected test results directory: {dev_tcr_dir.name}"
        )
        return

    inc_fields = optionals["include_fields"]
    exc_fields = optionals["exclude_fields"]
    inc_all = optionals["include_all"]

    filter_in = lambda i: i.get("field") in inc_fields
    filter_out = lambda i: i.get("field") not in exc_fields
    filter_fails = lambda i: i["status"] == trt.TestCaseStatus.FAIL

    for rc_result_file in test_result_files(device, optionals):

        # if the test results file does not exist, it means that the tests were
        # not executed.  For now, silently skip.  TODO: may show User warning?

        results_file = dev_tcr_dir.joinpath(f"{rc_result_file}.json")
        if not results_file.exists():
            continue

        results = json.load(results_file.open())

        if results[0]["status"] == trt.TestCaseStatus.SKIP:
            continue

        if not inc_all:
            results = filter(filter_fails, results)

        if exc_fields:
            results = filter(filter_out, results)

        if inc_fields:
            results = filter(filter_in, results)

        # display the results in a Table form.
        show_log_table(device, results_file.name, results)


def show_log_table(device: Device, filename: str, results: List[Dict]):
    console = Console()

    table = Table(
        "Status",
        "Device",
        "Id",
        "Field",
        "Log",
        title=f"Device: {device.name} Test Logs: {filename}",
        show_header=True,
        header_style="bold magenta",
        show_lines=True,
    )

    st_opt = trt.TestCaseStatus

    for result in results:
        r_st = result["status"]
        msr_val = _pretty_dict_table(result["measurement"])
        log_msg = (
            _pretty_dict_table(result["error"]) if r_st == st_opt.FAIL else msr_val
        )

        table.add_row(
            _colorize_status(result["status"]),
            device.name,
            result["test_case_id"],
            result.get("field"),
            log_msg,
        )

    console.print(table)


def _pretty_dict_table(obj):

    if not isinstance(obj, dict):
        return Pretty(obj)

    table = Table(show_header=False, box=None)
    for key, value in obj.items():
        table.add_row(key, Pretty(value))

    return table


def _colorize_status(status):
    options = trt.TestCaseStatus

    color = {options.PASS: "green", options.FAIL: "red", options.INFO: "blue"}.get(
        status
    )

    return f"[{color}]{status}[/{color}]"


def test_result_files(device, optionals: dict):
    inc_ts_names = optionals["testing_service_names"]

    for design_service in device.services:
        for testing_service in design_service.testing_services:
            ts_name = testing_service.get_service_name()

            if inc_ts_names:
                if ts_name in inc_ts_names:
                    yield ts_name

                continue

            yield ts_name
