# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------
import click
from rich.console import Console
from rich.table import Table, Text


# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device, interface_profile as ip

# CLI specific imports

from netcad.netcad_cli.common_opts import opt_devices
from netcad.netcad_cli.get_devices import get_devices
from .. import keywords
from .clig_design import clig_design_report

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def show_device_interfaces(device: Device, **options):
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Profile")
    table.add_column("Port")

    def add_row(*columns):
        table.add_row(*columns)

    # -------------------------------------------------------------------------
    # If the User only wants to see the unused interfaces ...
    # -------------------------------------------------------------------------

    if options["show_unused"]:
        for iface in sorted(device.interfaces.values()):
            if not iface.used:
                if_spec = device.device_type_spec.get_interface(if_name=iface.name)
                add_row(iface.name, None, keywords.NOT_USED, if_spec.if_type_label)

        console.print(table)
        return

    # -------------------------------------------------------------------------
    # Show interfaces, optionally including unused ....
    # -------------------------------------------------------------------------

    for iface in sorted(device.interfaces.values()):
        if not iface.used:
            if options["show_all"]:
                if_spec = device.device_type_spec.get_interface(if_name=iface.name)
                add_row(iface.name, None, keywords.NOT_USED, if_spec.if_type_label)
            continue

        if not (if_prof := getattr(iface, "profile", None)):
            add_row(iface.name, iface.desc, None, keywords.NOT_USED)
            continue

        if_prof_name = if_prof.name
        if not (port_prof := if_prof.port_profile):
            pp_name = keywords.MISSING
        else:
            pp_name = port_prof.name

        if isinstance(if_prof, ip.InterfaceVirtual):
            pp_name = keywords.VIRTUAL

        if_desc = Text(iface.desc, "yellow") if if_prof.is_reserved else iface.desc
        add_row(iface.name, if_desc, if_prof_name, pp_name)

    console.print(table)


@clig_design_report.command(name="interfaces")
@click.option(
    "--unused", "show_unused", help="only show unused interfaces", is_flag=True
)
@click.option(
    "--all", "show_all", help="show all interfaces, including unused", is_flag=True
)
@opt_devices(required=True)
def cli_design_report_interfaces(devices: Tuple[str], **flags):
    """
    report device interfaces usage

    \b
    The output includes the interface name, description, assigned profile, and
    physical port type.  By default this command will show only interfaces that
    are used in the design.  Any unused interfaces will be omitted.  Additonal
    flag options:
       --all : show the unused interfaces
       --unused : show only the unused interfaces

    \f
    Parameters
    ----------
    devices: tuple[str]
        A tuple of device names provided by the User
    """

    dev_objs = get_devices(device_list=devices)

    print(f"Checking {len(dev_objs)} devices ...")

    for each_dev in dev_objs:
        show_device_interfaces(each_dev, **flags)
