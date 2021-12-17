# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import json
from typing import Tuple, List, Dict
from pathlib import Path
from collections import Counter

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import click
from rich.table import Table, Text, Style
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
from netcad.cli.keywords import color_pass_fail

# -----------------------------------------------------------------------------
# Module Private Imports
# -----------------------------------------------------------------------------

from .cli_netcam_show import clig_show


# -----------------------------------------------------------------------------
# Exports (none)
# -----------------------------------------------------------------------------

__all__ = []


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@clig_show.command(name="tests")
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
@click.option("--info", "include_info", is_flag=True, help="include INFO reports")
@click.option(
    "--pass", "include_pass", is_flag=True, default=False, help="include PASS reports"
)
@click.option("--brief", "brief_mode", is_flag=True, help="Show summary counts only")
def cli_report_tests(devices: Tuple[str], designs: Tuple[str], **optionals):
    """Show test results in tablular form."""

    log = get_logger()

    if not (device_objs := get_devices_from_designs(designs, include_devices=devices)):
        log.error("No devices located in the given designs")
        return

    log.info(f"Showing test logs for {len(device_objs)} devices.")

    devices_tc_dirs = dict()
    for device in device_objs:
        dev_tcr_dir = netcad_globals.g_netcad_testcases_dir / device.name / "results"
        if not dev_tcr_dir.exists():
            log.error(
                f"Missing {device.name}, expected test results directory: {dev_tcr_dir.name}"
            )
            continue
        devices_tc_dirs[device] = dev_tcr_dir

    if not optionals["brief_mode"]:
        for dev_obj, dev_tc_dir in devices_tc_dirs.items():
            show_device_test_logs(dev_obj, dev_tc_dir, optionals)
    else:
        optionals["include_all"] = True
        for dev_obj, dev_tc_dir in devices_tc_dirs.items():
            show_device_brief_summary_table(dev_obj, dev_tc_dir, optionals)


# -----------------------------------------------------------------------------
#
#                              PRIVATE CODE BEGINS
#
# -----------------------------------------------------------------------------


def show_device_brief_summary_table(device: Device, tcr_dir: Path, optionals: dict):

    table = Table(
        "Test Cases",
        "Status",
        "Total",
        "Pass",
        "Fail",
        "Info",
        "Skip",
        show_header=True,
        header_style="bold magenta",
        show_lines=True,
    )

    pass_style = Style(color="green")
    fail_style = Style(color="red")
    info_style = Style(color="blue")
    skip_sytle = Style(color="magenta")

    dev_tc_count = 0
    for tc_name in find_test_cases_names(device, optionals):

        # if the test results file does not exist, it means that the tests were
        # not executed.  For now, silently skip.  TODO: may show User warning?

        results_file = tcr_dir.joinpath(f"{tc_name}.json")
        if not results_file.exists():
            continue

        results = json.load(results_file.open())

        if not (results := filter_results(results=results, optionals=optionals)):
            continue

        tcr_cntrs = Counter(res["status"] for res in results)
        tcr_total = sum(tcr_cntrs.values())
        dev_tc_count += tcr_total

        table.add_row(
            tc_name,
            color_pass_fail(tcr_cntrs),
            Text(str(tcr_total)),
            Text(str(tcr_cntrs[trt.TestCaseStatus.PASS]), style=pass_style),
            Text(str(tcr_cntrs[trt.TestCaseStatus.FAIL]), style=fail_style),
            Text(str(tcr_cntrs[trt.TestCaseStatus.INFO]), style=info_style),
            Text(str(tcr_cntrs[trt.TestCaseStatus.SKIP]), style=skip_sytle),
        )

    table.title = Text(
        f"Device: {device.name}, Total Results: {dev_tc_count}", justify="left"
    )
    console = Console()
    console.print("\n", table)


def filter_results(results: dict, optionals: dict) -> List[Dict]:
    """
    This function filters the test cases results based on the User CLI flags.

    Parameters
    ----------
    results:
        The complete list of test case results.

    optionals:
        The User CLI option flags

    Returns
    -------
    List of the filtered results.  If the results include a "skip" indicator,
    then an empty list is returned.
    """
    inc_all = optionals["include_all"]

    status_allows = {trt.TestCaseStatus.FAIL}

    inc_fields = optionals["include_fields"]
    exc_fields = optionals["exclude_fields"]

    if optionals["include_info"] or inc_all:
        status_allows.add(trt.TestCaseStatus.INFO)

    if optionals["include_pass"] or inc_all:
        status_allows.add(trt.TestCaseStatus.PASS)

    filter_flds_in = lambda i: i.get("field") in inc_fields
    filter_flds_out = lambda i: i.get("field") not in exc_fields
    filter_status = lambda i: i["status"] in status_allows

    results = filter(filter_status, results)

    if exc_fields:
        results = filter(filter_flds_out, results)

    if inc_fields:
        results = filter(filter_flds_in, results)

    return list(results)


def show_device_test_logs(device: Device, tcr_dir: Path, optionals: dict):

    for rc_result_file in find_test_cases_names(device, optionals):

        # if the test results file does not exist, it means that the tests were
        # not executed.  For now, silently skip.  TODO: may show User warning?

        results_file = tcr_dir.joinpath(f"{rc_result_file}.json")
        if not results_file.exists():
            continue

        results = json.load(results_file.open())

        if not (results := filter_results(results=results, optionals=optionals)):
            continue

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
        expected = result["test_case"]["expected_results"]
        r_st = result["status"]
        msr_val = _pretty_dict_table(
            dict(expected=expected, measured=result["measurement"])
        )

        if r_st == st_opt.FAIL:
            log_msg = _pretty_dict_table(result["error"])
        elif r_st == st_opt.SKIP:
            log_msg = result["message"]
        else:
            log_msg = msr_val

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

    color = {
        options.PASS: "green",
        options.FAIL: "red",
        options.INFO: "blue",
        options.SKIP: "magenta",
    }.get(status)

    return f"[{color}]{status}[/{color}]"


def find_test_cases_names(device, optionals: dict):
    inc_ts_names = optionals["testing_service_names"]

    for design_service in device.services.values():
        for testing_service in design_service.testing_services:
            ts_name = testing_service.get_service_name()

            if inc_ts_names:
                if ts_name in inc_ts_names:
                    yield ts_name

                continue

            yield ts_name
