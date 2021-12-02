# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple
from operator import attrgetter

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.table import Table, Text, Style
from rich.console import Console

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.config import netcad_globals
from netcad.device import Device, DeviceInterface
from netcad.device.interface_profile import InterfaceVirtual
from netcad.cabling.cable_plan import CablePlanner

from netcad.cli.netcad.clig_netcad_report import clig_design_report
from netcad.cli.device_inventory import get_devices_from_designs
from netcad.cli.common_opts import opt_devices, opt_designs

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@clig_design_report.command(name="cabling")
@opt_designs(required=True)
@opt_devices()
def cli_design_report_cabling(devices: Tuple[str], designs: Tuple[str]):
    """report cabling between devices"""

    log = get_logger()

    if not (device_objs := get_devices_from_designs(designs, include_devices=devices)):
        log.error("No devices located in the given designs")
        return

    # If specific devices were requested by the User, then report each device
    # separately.

    if devices:
        print(f"Reporting on {len(device_objs)} devices ...")
        for dev_obj in device_objs:
            report_cabling_per_device(dev_obj)

        return

    # If here, then the User did not request a specific device, but rather would
    # like to see the cabling report for all devices in each of the requested
    # designs.

    for design_name in designs:
        cabler: CablePlanner
        if not (cabler := CablePlanner.registry_get(name=design_name)):
            log.error(f"No cabling found for design: {design_name}")
            return

        report_cabling_per_network(network=design_name, cabling=cabler)


# -----------------------------------------------------------------------------
#
#                                 PRIVATE CODE BEGINS
#
# -----------------------------------------------------------------------------


NOT_USED = Text("UNUSED", style=Style(color="grey50"))
NOT_ASSIGNED = Text("N/A", style=Style(color="grey50"))
MISSING = Text("MISSING", style=Style(color="red"))
VIRTUAL = Text("virtual", style=Style(color="blue"))


def interface_profile_names(iface: DeviceInterface) -> Tuple[Text, Text]:
    if not iface.used:
        return NOT_USED, NOT_ASSIGNED

    if not (if_prof := iface.profile):
        return NOT_ASSIGNED, NOT_ASSIGNED

    if isinstance(if_prof, InterfaceVirtual):
        return if_prof.name, VIRTUAL

    if not (port_prof := if_prof.port_profile):
        return if_prof.name, MISSING

    return Text(if_prof.name), Text(port_prof.name)


def cabling_table(table: Table, cables) -> Table:

    for column in [
        "Device",
        "Interface",
        "Profile",
        "Port",
        "Remote Port",
        "Remote Profile",
        "Remote Interface",
        "Remote Device",
        "Cable-ID",
    ]:

        table.add_column(column)

    for cable_id, dev_if, rmt_if in cables:

        dev_if_prof, dev_phy_prof = interface_profile_names(dev_if)
        rmt_if_prof, rmt_phy_prof = interface_profile_names(rmt_if)

        # if the physical port definitions are not the same, then color them in
        # red to indicate the error to the User.

        if dev_phy_prof != rmt_phy_prof:
            dev_phy_prof.style = Style(color="red")
            rmt_phy_prof.style = Style(color="red")

        table.add_row(
            dev_if.device.name,
            dev_if.name,
            dev_if_prof,
            dev_phy_prof,
            rmt_phy_prof,
            rmt_if_prof,
            rmt_if.name,
            rmt_if.device.name,
            cable_id,
        )

    return table


def report_cabling_per_device(device: Device):
    console = Console()

    cables = [
        (interface.cable_id, interface, interface.cable_peer)
        for interface in device.interfaces.values()
        if interface.cable_peer
    ]

    table = cabling_table(
        table=Table(
            title=f"Device Cabling: {device.name}",
            show_header=True,
            header_style="bold magenta",
        ),
        cables=cables,
    )

    console.print(table)


def report_cabling_per_network(cabling: CablePlanner, network: str):
    console = Console()

    if not cabling.cables:
        console.print(f"[yellow]{network}: No cables.[/yellow]")
        return

    design = netcad_globals.g_netcad_designs[network]
    design_desc = design.get("description") or ""

    # orient each cable row (left-device, right-device) based on their sorting
    # property (User defined, or hostname by default)

    cables = [
        [cable[0], *sorted(cable[1], key=attrgetter("device"))]
        for cable in cabling.cables.items()
    ]

    # then sort the table based on the device-name, and interface sort-key

    cables.sort(key=lambda c: (c[1].device.name, c[1], c[2].device.name, c[2]))

    table = cabling_table(
        table=Table(
            title=f"Design Cabling '{network}', {design_desc}",
            show_header=True,
            header_style="bold magenta",
        ),
        cables=cables,
    )

    console.print(table)
