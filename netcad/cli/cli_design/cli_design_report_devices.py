# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple, List

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
from netcad.device import Device

from netcad.cli.common_opts import opt_network
from netcad.cli.device_inventory import get_network_devices

from .clig_design import clig_design_report

# -----------------------------------------------------------------------------
# Exports (none)
# -----------------------------------------------------------------------------

__all__ = []


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def show_network_devices(network: str, devices: List[Device], **flags):
    console = Console()

    table = Table(
        show_header=True, header_style="bold magenta", title=f"Network: {network}"
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
@opt_network(required=True)
@click.option("--all", "include_pseudo", help="show pseudo devices", is_flag=True)
def cli_design_report_devices(networks: Tuple[str], **flags):
    """
    report network device usage

    This command will report on the devices in each of the networks provided, a
    separate table per network.  If a network contains "pseudo" devices, for
    example redundant MLAG-pair, these devices will not be included in the
    report unless the --all option is specified.

    \f
    Parameters
    ----------
    networks: tuple[str]
        Names of networks

    Other Parameters
    ----------------
    include_pseduo: bool, optional, default False
        When True the report will include pseudo devices, such as redundant MLAG
        pairs.
    """

    log = get_logger()
    network_devices = dict()
    total_devs = 0

    for each_net in networks:
        net_devs = network_devices[each_net] = sorted(get_network_devices((each_net,)))
        if not net_devs:
            log.info("No devices found in the given networks")
            return
        total_devs += len(net_devs)

    log.info(f"Reporting on {len(networks)} networks, {total_devs} devices.")
    for net_name, net_devs in network_devices.items():
        show_network_devices(net_name, net_devs, **flags)
