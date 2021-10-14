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

from netcad.device import Device
from netcad.config import loader
from .main import clig_design_report
from .common_opts import opt_devices


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def show_device_interfaces(device: Device):
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name")
    table.add_column("Interface-Profile")
    table.add_column("Port-Profile")

    for iface in device.sorted_interfaces():
        if not (if_prof := iface.profile):
            pp_name = "[yellow]NONE[/yellow]"
            if_prof_name = "NONE"
        else:
            if_prof_name = if_prof.name
            if not (port_prof := if_prof.port_profile):
                pp_name = "[red]MISSING[/red]"
            else:
                pp_name = port_prof.name

        if not iface.used:
            if_prof_name = "[yellow]UNUSED[/yellow]"

        table.add_row(iface.name, if_prof_name, pp_name)

    console.print(table)


@clig_design_report.command(name="interfaces")
@opt_devices(required=True)
@click.pass_context
def cli_design_report_interfaces(ctx: click.Context, devices: Tuple[str]):
    """report device interface usage and parts"""

    netcad_config = loader.load()
    loader.network_importer(netcad_config)

    dev_objs: List[Device] = list()

    for dev_name in set(devices):
        if not (dev_obj := Device.registry_get(dev_name)):
            ctx.fail(f"Device not found in registry: {dev_name}")
            return
        dev_objs.append(dev_obj)

    print(f"Checking {len(dev_objs)} devices ...")
    for each_dev in dev_objs:
        show_device_interfaces(each_dev)
