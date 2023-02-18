#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import TYPE_CHECKING

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

if TYPE_CHECKING:
    from netcad.device import DeviceInterface

from netcad.helpers import range_string

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["j2_vlans_id_list", "range_string"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def j2_vlans_id_list(if_obj: "DeviceInterface", adj_sep=None) -> str:
    if not (vlans := getattr(if_obj.profile, "trunk_allowed_vlans", None)):
        dev_name = if_obj.device.name
        if_name = if_obj.name
        raise RuntimeError(f"{dev_name}:{if_name} does not have assigned vlans")

    return range_string(
        numbers=sorted([vlan.vlan_id for vlan in vlans()]), adj_sep=adj_sep
    )
