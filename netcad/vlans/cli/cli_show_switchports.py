#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.console import Console
from rich.table import Table

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.device import Device
from netcad.vlans.profiles.l2_interfaces import InterfaceL2Access, InterfaceL2Trunk
from netcad.cli.device_inventory import get_devices_from_designs
from netcad.cli.common_opts import opt_devices, opt_designs

# -----------------------------------------------------------------------------
# Module Private Imports
# -----------------------------------------------------------------------------

from netcad.cli.netcad.clig_netcad_show import clig_design_show

# -----------------------------------------------------------------------------
# Exports (none)
# -----------------------------------------------------------------------------

__all__ = []

# -----------------------------------------------------------------------------
#
#                            CLI CODE BEGINS
#
# -----------------------------------------------------------------------------


@clig_design_show.command(name="switchports")
@opt_designs()
@opt_devices()
def cli_report_vlans(devices: Tuple[str], designs: Tuple[str]):
    """
    show interface switchports used by design
    """
    log = get_logger()

    if not (
        dev_objs := get_devices_from_designs(designs=designs, include_devices=devices)
    ):
        log.error("No devices located in the given designs")
        return

    print(f"Showing {len(dev_objs)} devices ...")
    for dev in dev_objs:
        show_device_switchports_table(dev)


# -----------------------------------------------------------------------------
#
#                            PRIVATE CODE BEGINS
#
# -----------------------------------------------------------------------------


def show_device_switchports_table(device: Device):

    # each device instance may have one or more device-vlan design services.
    # Typically, it will be one, but perhaps a Designer comes up with a usage
    # that does have more than one.  So handle that, just in case ;-)

    console = Console()

    table = Table(
        "Interface",
        "Description",
        "Profile",
        "Switchport\nMode",
        "Access/Native VLAN",
        "Trunk Allowed VLANs",
        title_justify="left",
        show_header=True,
        show_lines=True,
        header_style="bold magenta",
    )

    def fmt_vlan(_vlan):
        return f"{_vlan.vlan_id:>4} ({_vlan.name})"

    for intf_obj in sorted(device.interfaces.used().values()):

        if isinstance(intf_obj.profile, InterfaceL2Access):
            swp_p = intf_obj.profile
            vlan = swp_p.vlan
            table.add_row(
                intf_obj.name,
                intf_obj.desc,
                intf_obj.profile.name,
                "access",
                fmt_vlan(vlan),
                "",
            )
            continue

        if isinstance(intf_obj.profile, InterfaceL2Trunk):
            swp_p = intf_obj.profile
            nvlan = swp_p.native_vlan
            allowed = "\n".join(
                [fmt_vlan(vlan) for vlan in sorted(swp_p.trunk_allowed_vlans())]
            )

            table.add_row(
                intf_obj.name,
                intf_obj.desc,
                intf_obj.profile.name,
                "trunk",
                fmt_vlan(nvlan),
                allowed,
            )
            continue

    table.title = f"Device: {device.name}, Switchports ({len(table.rows)})"
    console.print("\n", table if table.rows else table.title)
