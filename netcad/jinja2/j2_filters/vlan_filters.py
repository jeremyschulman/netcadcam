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


def j2_vlans_id_list(if_obj: "DeviceInterface") -> str:

    if not (vlans := getattr(if_obj.profile, "vlans", None)):
        dev_name = if_obj.device.name
        if_name = if_obj.name
        raise RuntimeError(f"{dev_name}:{if_name} does not have assigned vlans")

    # do not include the native vlan in the range-list.
    if native_vlan := getattr(if_obj.profile, "native_vlan", None):
        vlans = set(vlans) - {native_vlan}

    return range_string(numbers=sorted([vlan.vlan_id for vlan in vlans]))
