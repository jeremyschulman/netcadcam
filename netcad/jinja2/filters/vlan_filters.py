# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import DeviceInterface
from netcad.helpers import range_string

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["j2_filter_vlans_id_list"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def j2_filter_vlans_id_list(if_obj: DeviceInterface) -> str:

    if not (vlans := getattr(if_obj.profile, "vlans", None)):
        dev_name = if_obj.device.name
        if_name = if_obj.name
        raise RuntimeError(f"{dev_name}:{if_name} does not have assigned vlans")

    return range_string(numbers=[vlan.vlan_id for vlan in vlans])
