# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import asyncio
from typing import Tuple, Dict
from pathlib import Path
from datetime import datetime
from collections import Counter

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import click
from rich.console import Console
from rich.text import Text, Style
from rich.table import Table

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import Environment, netcad_globals
from netcad.logger import get_logger
from netcad.netcam.dut import DeviceUnderTest
from netcad.cli.common_opts import opt_devices, opt_designs
from netcad.cli.device_inventory import get_devices_from_designs

from netcad.netcam.loader import import_netcam_plugin

from netcad.cli.netcam.cli_netcam_main import cli
from netcad.netcam import execute_testcases
from netcad.cli.keywords import color_pass_fail


# -----------------------------------------------------------------------------
# Exports (none)
# -----------------------------------------------------------------------------

__all__ = []


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@cli.command(name="test")
@opt_devices()
@opt_designs(required=True)
@click.option(
    "--tests-dir",
    help="location to read test-cases",
    type=click.Path(path_type=Path, resolve_path=True, exists=True, writable=True),
    envvar=Environment.NETCAD_TESTCASESDIR,
)
def cli_test_device(devices: Tuple[str], designs: Tuple[str], tests_dir: Path):
    """
    Execute tests to validate the operational state of devices.

    This command will use the device test cases to validate the running state
    compared to the expected states defined by the tests.

    \f
    Parameters
    ----------
    designs:
        The list of design names that should be processed by this command. All
        devices within the design will be processed, unless further filtered by
        the `devices` option.

    devices:
        The list of deice hostnames that should be processed by this command.

    tests_dir:
        The Path instance to the parent directory of test-cases.  Subdirectories
        exist for each device by hostname.
    """

    log = get_logger()

    netcam_plugins = import_netcam_plugin()

    if not (device_objs := get_devices_from_designs(designs, include_devices=devices)):
        log.error("No devices located in the given designs")
        return

    # create the device-under-test (DUT) instances for each of the devices in
    # the design. we keep this collection as a dictionary so that we can refer
    # back to the DUT by device name when be build the summary table.

    tc_dir = netcad_globals.g_netcad_testcases_dir
    duts = {}

    for dev_obj in device_objs:
        if not (pg_cfg := netcam_plugins.get(dev_obj.os_name)):
            raise RuntimeError(
                f"Missing testing plugin for {dev_obj.name}: os-name: {dev_obj.os_name}"
            )

        duts[dev_obj.name] = pg_cfg.get_dut(
            device=dev_obj, testcases_dir=tc_dir.joinpath(dev_obj.name)
        )

    log.info(f"Starting tests for {len(device_objs)} devices.")

    # execute the tests concurrently to minimize the time it takes to run
    # though all of the tests.

    # TODO: this _presumes_ that the underlying "netcam" plugin was written to
    #       support asyncio.  This might not always be the case, so need to put
    #       in a check and execute the plugin running differently. For now, only
    #       asyncio plugins are supported.

    ts_start = datetime.now()

    async def go():
        await asyncio.gather(*(execute_testcases(dut) for dut in duts.values()))

    asyncio.run(go())
    ts_end = datetime.now()

    display_summary_table(duts, duration=ts_end - ts_start)


# -----------------------------------------------------------------------------
#
#                          PRIVATE CODE BEGINS
#
# -----------------------------------------------------------------------------


def display_summary_table(duts: Dict[str, DeviceUnderTest], duration):
    # Display summary table for each device, and then a grand total summary

    table = Table(
        "Device",
        "Status",
        "Total",
        "Pass",
        "Fail",
        "Info",
        show_header=True,
        header_style="bold magenta",
        show_lines=True,
    )

    colored_styles = (Style(color="green"), Style(color="red"), Style(color="blue"))
    grand_totals = Counter()

    for dut in sorted(duts.values()):
        cntrs = dut.result_counts
        grand_totals.update(cntrs)

        totals = str(sum(cntrs.values()))
        clrd_cnts = [
            Text(str(cntr), style=clrd_style)
            for cntr, clrd_style in zip(
                (cntrs["PASS"], cntrs["FAIL"], cntrs["INFO"]), colored_styles
            )
        ]
        table.add_row(dut.device.name, color_pass_fail(cntrs), totals, *clrd_cnts)

    gt_sum = sum(grand_totals.values())

    console = Console()
    pass_fail = color_pass_fail(grand_totals)

    console.print(
        "\n",
        "Overall Test Results: ",
        pass_fail,
        "\n",
        f"{len(duts)} Devices, {gt_sum} Testscases\n",
        f"Duration {duration}\n",
    )

    table.title = Text("Device Summaries", justify="left")
    console.print(table, "\n")
