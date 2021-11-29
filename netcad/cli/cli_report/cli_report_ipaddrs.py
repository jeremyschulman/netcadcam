# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple, List

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.table import Table
from rich.console import Console

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.device import DeviceInterface, Device
from netcad.device.l3_interfaces import InterfaceL3
from ..common_opts import opt_devices, opt_designs
from ..device_inventory import get_devices_from_designs
from netcad.cli.netcad.clig_netcad_report import clig_design_report


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@clig_design_report.command(name="ipaddrs")
@opt_designs(required=True)
@opt_devices()
def cli_design_report_interfaces(devices: Tuple[str], designs: Tuple[str]):
    """
    report IP addresses used in design.

    \f
    Parameters
    ----------
    devices
    designs
    """
    log = get_logger()

    if not (
        dev_objs := get_devices_from_designs(designs=designs, include_devices=devices)
    ):
        log.error("No devices located in the given designs")
        return

    print(f"Checking {len(dev_objs)} devices ...")

    # Generate the list of interfaces with IP addresses.  These must be
    # interfaces with profiles that subclass InterfaceL3.

    if_l3_list = [
        (dev, iface)
        for dev in dev_objs
        for iface in dev.interfaces.used().values()
        if isinstance(iface.profile, InterfaceL3) and iface.profile.if_ipaddr
    ]

    report_l3_interfaces(if_l3_list)


# -----------------------------------------------------------------------------
#
#                               PRIVATE CODE BEGINS
#
# -----------------------------------------------------------------------------


def report_l3_interfaces(interfaces: List[Tuple[Device, DeviceInterface]]):
    console = Console()

    # For now, just one big table.  We could separate this into device tables,
    # IP subnet tables, etc.  For now sorting by: IP address, then by device; so
    # that the IP addresses are arranged in sorted increasing order.

    interfaces.sort(key=lambda i: (i[1].profile.if_ipaddr, i[0]))

    table = Table(
        "Device",
        "Interface",
        "Description",
        "IP Address",
        title="IP addresses",
        show_header=True,
        header_style="bold magenta",
    )

    for dev, iface in interfaces:
        table.add_row(dev.name, iface.name, iface.desc, str(iface.profile.if_ipaddr))

    console.print(table)
