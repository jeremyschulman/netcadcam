# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple, Iterable

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import click
from rich.console import Console
from rich.table import Table

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.config import netcad_globals
from netcad.device import Device
from netcad.cabling.cable_plan import CablePlanner

from .clig_netcad_report import clig_design_report
from ..common_opts import opt_designs
from ..device_inventory import get_devices_from_designs

# -----------------------------------------------------------------------------
# Exports (none)
# -----------------------------------------------------------------------------

__all__ = []


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def show_network_devices(network: str, devices: Iterable[Device], **flags):
    console = Console()
    design = netcad_globals.g_netcad_designs[network]
    design_desc = design.get("description") or ""

    table = Table(
        show_header=True,
        header_style="bold magenta",
        title=f"Design '{network}', {design_desc}",
    )
    table.add_column("Device")
    table.add_column("OS Name")
    table.add_column("Product Model")
    table.add_column("Profile")

    for dev in devices:
        dev_type = dev.__class__.__name__

        # if the device is pseudo, and the User requested these to be shown,
        # then include them with a blue-color-style.  Otherwise skip this
        # device.

        if dev.is_pseudo:
            if not flags["include_pseudo"]:
                continue
            dev_type = f"[blue]{dev_type}[/blue]"

        table.add_row(dev.name, dev.os_name, dev.product_model, dev_type)

    console.print("\n", table)


@clig_design_report.command(name="devices")
@opt_designs(required=True)
@click.option("--all", "include_pseudo", help="show pseudo devices", is_flag=True)
def cli_design_report_devices(designs: Tuple[str], **flags):
    """
    report network device usage

    This command will report on the devices in each of the networks provided, a
    separate table per network.  If a network contains "pseudo" devices, for
    example redundant MLAG-pair, these devices will not be included in the
    report unless the --all option is specified.

    \f
    Parameters
    ----------
    designs: tuple[str]
        Names of networks

    Other Parameters
    ----------------
    include_pseduo: bool, optional, default False
        When True the report will include pseudo devices, such as redundant MLAG
        pairs.
    """

    log = get_logger()

    if not (device_objs := get_devices_from_designs(designs=designs)):
        log.error("No devices located in the given designs")
        return

    log.info(f"Reporting on {len(designs)} designs, {len(device_objs)} devices.")

    for design_name in designs:
        cabler: CablePlanner
        if not (cabler := CablePlanner.registry_get(name=design_name)):
            log.error(f"No cabling found for design: {design_name}")
            return

        show_network_devices(design_name, cabler.devices, **flags)
