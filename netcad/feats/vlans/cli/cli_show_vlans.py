#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple
from collections import defaultdict
from itertools import chain

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.console import Console
from rich.table import Table
from rich.console import Pretty

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.device import Device
from netcad.feats.vlans.vlan_feat import DeviceVlanDesignFeature

from netcad.cli.device_inventory import get_devices_from_designs
from netcad.cli.common_opts import opt_devices, opt_designs

# -----------------------------------------------------------------------------
# Module Private Imports
# -----------------------------------------------------------------------------

from netcad.cli.clig_netcad_show import clig_design_show

# -----------------------------------------------------------------------------
# Exports (none)
# -----------------------------------------------------------------------------

__all__ = []

# -----------------------------------------------------------------------------
#
#                            CLI CODE BEGINS
#
# -----------------------------------------------------------------------------


@clig_design_show.command(name="vlans")
@opt_designs()
@opt_devices()
def cli_report_vlans(devices: Tuple[str], designs: Tuple[str]):
    """
    show VLANs used by design
    """
    log = get_logger()

    if not (
        dev_objs := get_devices_from_designs(designs=designs, include_devices=devices)
    ):
        log.error("No devices located in the given designs")
        return

    print(f"Showing {len(dev_objs)} devices ...")
    for dev in dev_objs:
        show_device_vlan_table(dev)


# -----------------------------------------------------------------------------
#
#                            PRIVATE CODE BEGINS
#
# -----------------------------------------------------------------------------


def show_device_vlan_table(device: Device, quiet=True):
    # each device instance may have one or more device-vlan design features.
    # Typically, it will be one, but perhaps a Designer comes up with a usage
    # that does have more than one.  So handle that, just in case ;-)

    console = Console()

    vlans = list(
        chain.from_iterable(
            svc.all_vlans() for svc in device.services_of(DeviceVlanDesignFeature)
        )
    )

    title = f"Device: {device.name}, VLANS ({len(vlans)})"

    if not vlans:
        if not quiet:
            console.print("\n", title)
        return

    table = Table(
        "VLAN-ID",
        "VLAN Name",
        "Interfaces",
        title=title,
        title_justify="left",
        show_header=True,
        header_style="bold magenta",
    )

    # correlate the vlans to each used by interfaces

    vlan_interfaces = defaultdict(list)
    for iface in device.interfaces.used().values():
        if not (vlans_used := getattr(iface.profile, "vlans_used", None)):
            continue
        for vlan in vlans_used():
            vlan_interfaces[vlan].append(iface)

    for vlan in vlans:
        if interfaces := vlan_interfaces.get(vlan):
            interfaces = [iface.name for iface in sorted(interfaces)]

        table.add_row(str(vlan.vlan_id), vlan.name, Pretty(interfaces))

    console.print("\n", table)
