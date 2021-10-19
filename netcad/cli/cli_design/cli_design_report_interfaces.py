# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------
import click
from rich.console import Console
from rich.table import Table


# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad import interface_profile as ip

# CLI specific imports

from netcad.cli.main import clig_design_report
from netcad.cli.common_opts import opt_devices
from netcad.cli.get_devices import get_devices


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def show_device_interfaces(device: Device, show_unused: bool):
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Interface-Profile")
    table.add_column("Port-Profile")

    for iface in device.sorted_interfaces():
        if not (if_prof := iface.profile):
            pp_name = None  # , "[yellow]NONE[/yellow]"
            if_prof_name = "NONE"
        else:
            if_prof_name = if_prof.name
            if not (port_prof := if_prof.port_profile):
                pp_name = "[red]MISSING[/red]"
            else:
                pp_name = port_prof.name

            if isinstance(if_prof, ip.InterfaceVirtual):
                pp_name = "[blue]   virtual[/blue]"

        if not iface.used:
            if_prof_name = "[yellow]   unused[/yellow]"

        table.add_row(iface.name, iface.desc, if_prof_name, pp_name)

    console.print(table)


@clig_design_report.command(name="interfaces")
@click.option(
    "--unused", "show_unused", help="only show unused interfaces", is_flag=True
)
@opt_devices(required=True)
def cli_design_report_interfaces(devices: Tuple[str], show_unused: bool):
    """report device interface usage and parts"""

    dev_objs = get_devices(device_list=devices)

    print(f"Checking {len(dev_objs)} devices ...")

    for each_dev in dev_objs:
        show_device_interfaces(each_dev, show_unused)
