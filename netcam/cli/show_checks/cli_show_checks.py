#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple
from pathlib import Path
from itertools import groupby
import shutil

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import click
from rich.console import Console

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import Environment, netcad_globals
from netcad.logger import get_logger

from netcad.cli.common_opts import opt_devices, opt_designs
from netcad.cli.device_inventory import get_devices_from_designs


from ..cli_netcam_show import clig_show
from .show_device_brief_table import show_device_brief_table
from .show_device_check_logs import show_device_test_logs
from .show_design_summary import show_design_summary_table

# -----------------------------------------------------------------------------
# Exports (none)
# -----------------------------------------------------------------------------

__all__ = []


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@clig_show.command(name="check")
@opt_devices()
@opt_designs()
@click.option(
    "--checks-dir",
    help="location to read checks",
    type=click.Path(path_type=Path, resolve_path=True, exists=True, writable=True),
    envvar=Environment.NETCAD_CHECKSDIR,
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
    "--check",
    "testing_service_names",
    multiple=True,
    help="display only logs from <test>",
)
@click.option(
    "--service",
    "service_list",
    multiple=True,
    help="execute only these design checks",
)
@click.option(
    "--all", "include_all", is_flag=True, help="display all results, not just FAIL"
)
@click.option("--info", "include_info", is_flag=True, help="include INFO reports")
@click.option(
    "--pass", "include_pass", is_flag=True, default=False, help="include PASS reports"
)
@click.option(
    "--passing", "pass_only", is_flag=True, default=False, help="Only show PASS reports"
)
@click.option(
    "--brief", "brief_mode", is_flag=True, help="Show summary counts of device(s)"
)
@click.option(
    "--summary", "summary_mode", is_flag=True, help="Show summary counts of design(s)"
)
def cli_report_tests(
    devices: Tuple[str], designs: Tuple[str], checks_dir: Path, **optionals
):
    """Show check results in tablular form."""

    log = get_logger()

    if not (device_objs := get_devices_from_designs(designs, include_devices=devices)):
        log.error("No devices located in the given designs")
        return

    device_objs = [
        dev for dev in device_objs if not any((dev.is_pseudo, dev.is_not_managed))
    ]

    log.info(f"Showing test logs for {len(device_objs)} devices.")

    # bind a test-case-dir Path attribute (tcr_dir) to each Device instance so
    # that the results can be retrieved and processed.

    tc_dir = checks_dir or netcad_globals.g_netcad_checks_dir

    for device in device_objs:
        dev_tcr_dir = tc_dir / device.design.name / device.name / "results"

        # 'stick' a new attribute onto the Device instance that will be
        # privately used within this CLI module.

        device.tcr_dir = dev_tcr_dir
        if not dev_tcr_dir.exists():
            log.error(
                f"Missing {device.name}, expected test results directory: {dev_tcr_dir.name}"
            )
            continue

    devices_by_design = groupby(
        sorted(device_objs, key=lambda d: id(d.design)), key=lambda d: d.design
    )

    term_sz = shutil.get_terminal_size()
    console = Console(record=True, width=term_sz.columns)

    # -------------------------------------------------------------------------
    # Option --brief
    # -------------------------------------------------------------------------

    if optionals["brief_mode"]:
        optionals["include_all"] = True

        for design, device_objs in devices_by_design:
            show_design_summary_table(
                console=console, design=design, optionals=optionals, devices=devices
            )

        return

    # -------------------------------------------------------------------------
    # Option --brief
    # -------------------------------------------------------------------------

    if optionals["summary_mode"]:
        optionals["include_all"] = True

        for design, device_objs in devices_by_design:
            for dev_obj in device_objs:
                show_device_brief_table(console, dev_obj, optionals)

        # done with brief mode, exit CLI processing
        return

    # -------------------------------------------------------------------------
    # Full reporting mode
    # -------------------------------------------------------------------------

    for design, device_objs in devices_by_design:
        for dev_obj in device_objs:
            show_device_test_logs(console, dev_obj, optionals)

    console.save_html(path="log.html")
