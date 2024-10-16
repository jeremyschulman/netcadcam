#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.table import Table, Text, Style
from rich.console import Console

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.device import Device, DeviceInterface
from netcad.phy_port import PhyPortProfile
from netcad.device.profiles.interface_profile import InterfaceVirtual

from netcad.cli.clig_netcad_show import clig_design_show
from netcad.cli.device_inventory import get_devices_from_designs
from netcad.cli.common_opts import opt_devices, opt_designs

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@clig_design_show.command(name="cabling")
@opt_designs()
@opt_devices()
def cli_design_report_cabling(devices: Tuple[str], designs: Tuple[str]):
    """show cabling between devices"""

    log = get_logger()

    if not (device_objs := get_devices_from_designs(designs, include_devices=devices)):
        log.error("No devices located in the given designs")
        return

    log.info(f"Reporting on {len(device_objs)} devices ...")

    if devices:
        for dev_obj in device_objs:
            report_cabling_per_device(dev_obj)
    else:
        report_cabling_per_network(device_objs)


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

    if not (port_prof := if_prof.phy_profile):
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
        # "Cable-ID",
    ]:
        table.add_column(column)

    def phy_is_different(lcl_phy: PhyPortProfile, rmt_phy: PhyPortProfile) -> bool:
        # if no phy-ports, then return not-different ;-)
        if lcl_phy is None and rmt_phy is None:
            return False

        try:
            return not all(
                (
                    lcl_phy.speed == rmt_phy.speed,
                    lcl_phy.cabling.media == rmt_phy.cabling.media,
                )
            )
        except (AttributeError, TypeError):
            return True

    def phy_is_not_exactly_same(
        lcl_phy: PhyPortProfile, rmt_phy: PhyPortProfile
    ) -> bool:
        if lcl_phy is None and rmt_phy is None:
            return False

        return lcl_phy != rmt_phy

    # -------------------------------------------------------------------------
    # create each cabling row
    # -------------------------------------------------------------------------

    dev_if: DeviceInterface
    rmt_if: DeviceInterface

    for cable_id, dev_if, rmt_if in cables:
        dev_if_prof, dev_phy_prof = interface_profile_names(dev_if)
        rmt_if_prof, rmt_phy_prof = interface_profile_names(rmt_if)

        # if the physical port definitions are not the same, then color them in
        # red to indicate the error to the User.

        # if the interfaces are designed to be disabled, then do not include
        # them in the cabling table.

        if not all((dev_if.enabled, rmt_if.enabled)):
            pass
            # continue

        elif all((dev_if.profile, rmt_if.profile)) and phy_is_different(
            dev_if.profile.phy_profile, rmt_if.profile.phy_profile
        ):
            dev_phy_prof.style = Style(color="red")
            rmt_phy_prof.style = Style(color="red")

        elif all((dev_if.profile, rmt_if.profile)) and phy_is_not_exactly_same(
            dev_if.profile.phy_profile, rmt_if.profile.phy_profile
        ):
            dev_phy_prof.style = Style(color="yellow")
            rmt_phy_prof.style = Style(color="yellow")

        table.add_row(
            dev_if.device.name,
            dev_if.name,
            dev_if_prof,
            dev_phy_prof,
            rmt_phy_prof,
            rmt_if_prof,
            rmt_if.name,
            rmt_if.device.name,
            # cable_id,
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


def report_cabling_per_network(devices: dict[str, Device]):
    console = Console()
    design = next(iter(devices)).design
    design_desc = design.config.get("description", "")

    device: Device
    cables = [
        (interface.cable_id, interface, interface.cable_peer)
        for device in devices
        if not device.is_pseudo
        for interface in device.interfaces.values()
        if interface.cable_peer and not interface.cable_peer.device.is_pseudo
    ]

    # then sort the table based on the device-name, and interface sort-key

    cables.sort(key=lambda c: (c[1].device, c[1], c[2].device, c[2]))

    table = cabling_table(
        table=Table(
            title=f"Design Cabling '{design.name}', {design_desc}",
            title_justify="left",
            show_header=True,
            header_style="bold magenta",
        ),
        cables=cables,
    )

    console.print(table)
