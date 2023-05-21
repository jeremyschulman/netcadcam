#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

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
from netcam.dut import DeviceUnderTest
from netcad.cli.common_opts import opt_devices, opt_designs
from netcad.cli.device_inventory import get_devices_from_designs

# from netcad.netcam.loader import import_netcam_plugins

from netcam.cli import cli

from netcam.execute_checks import (
    execute_device_checks,
    cv_check_list,
    cv_service_list,
)
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


@cli.command(name="check")
@opt_devices()
@opt_designs()
@click.option(
    "--check",
    "check_list",
    multiple=True,
    help="execute only these design checks",
)
@click.option(
    "--service",
    "service_list",
    multiple=True,
    help="execute only these design checks",
)
@click.option(
    "--checks-dir",
    help="location to read device checks",
    type=click.Path(path_type=Path, resolve_path=True, exists=True, writable=True),
    envvar=Environment.NETCAD_CHECKSDIR,
)
def cli_test_device(
    devices: Tuple[str],
    designs: Tuple[str],
    check_list: Tuple[str],
    checks_dir: Path,
    service_list: Tuple[str],
):
    """
    Execute checks to validate the operational state of devices.

    This command will use the device checks to validate the running state
    compared to the expected states defined by the design via the "netcad build
    checks ..." command.

    \f
    Parameters
    ----------
    designs:
        The list of design names that should be processed by this command. All
        devices within the design will be processed, unless further filtered by
        the `devices` option.

    devices:
        The list of deice hostnames that should be processed by this command.

    check_list: optional
        The list of design checks to execute, if provided.  For example
        "interfaces".  Otherwise, all checks are run.

    service_list: optional,
        Similar to check_list, but higher level design service names, like
        "topology".

    checks_dir:
        The Path instance to the parent directory of checks.  Subdirectories
        exist for each device by hostname.
    """

    log = get_logger()

    if not (device_objs := get_devices_from_designs(designs, include_devices=devices)):
        log.error("No devices located in the given designs")
        return

    device_objs = [
        dev for dev in device_objs if not any((dev.is_pseudo, dev.is_not_managed))
    ]

    # create the device-under-test (DUT) instances for each of the devices in
    # the design. we keep this collection as a dictionary so that we can refer
    # back to the DUT by device name when be build the summary table.

    tc_dir = checks_dir or netcad_globals.g_netcad_checks_dir
    netcam_plugins = netcad_globals.g_netcam_plugins_os_catalog

    duts = {}

    async def run_tests():
        cv_check_list.set(check_list)
        cv_service_list.set(service_list)

        for dev_obj in device_objs:
            if not (pg_obj := netcam_plugins.get(dev_obj.os_name)):
                log.error(
                    f"Missing testing plugin for {dev_obj.name}: os-name: {dev_obj.os_name}, skipping."
                )
                continue

            duts[dev_obj] = dut_obj = pg_obj.module.plugin_get_dut(device=dev_obj)

            # the device checks directory is subdir under the design name.
            dut_obj.testcases_dir = tc_dir / dev_obj.design.name / dev_obj.name

        remove_unsupported = [dev for dev, dut in duts.items() if not dut]
        for dev_obj in remove_unsupported:
            log.warning(f"Missing DUT support for device: {dev_obj.name}, skipping.")

        for dev_obj in remove_unsupported:
            del duts[dev_obj]

        log.info(f"Starting tests for {len(duts)} devices.")

        # execute the tests concurrently to minimize the time it takes to run
        # through all the tests.

        # TODO: this _presumes_ that the underlying "netcam" plugin was written to
        #       support asyncio.  This might not always be the case, so need to put
        #       in a check and execute the plugin running differently. For now, only
        #       asyncio plugins are supported.

        await asyncio.gather(*(execute_device_checks(dut) for dut in duts.values()))

    ts_start = datetime.now()
    asyncio.run(run_tests())
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
        "Skip",
        show_header=True,
        header_style="bold magenta",
        show_lines=True,
    )

    colored_styles = (
        Style(color="green"),
        Style(color="red"),
        Style(color="blue"),
        Style(color="magenta"),
    )

    grand_totals = Counter()

    for dut in sorted(duts.values()):
        cntrs = dut.result_counts
        grand_totals.update(cntrs)

        totals = str(sum(cntrs.values()))
        clrd_cnts = [
            Text(str(cntr), style=clrd_style)
            for cntr, clrd_style in zip(
                (cntrs["PASS"], cntrs["FAIL"], cntrs["INFO"], cntrs["SKIP"]),
                colored_styles,
            )
        ]
        table.add_row(dut.device.name, color_pass_fail(cntrs), totals, *clrd_cnts)

    gt_sum = sum(grand_totals.values())

    console = Console()
    pass_fail = color_pass_fail(grand_totals)

    console.print(
        "\n",
        "Overall Check Results: ",
        pass_fail,
        "\n",
        f"{len(duts)} Devices, {gt_sum} Checks\n",
        f"Duration {duration}\n",
    )

    table.title = Text("Device Summaries", justify="left")
    console.print(table, "\n")
