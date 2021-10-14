# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import typing as t

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.vlan_profile import VlanProfile, SENTIAL_ALL_VLANS
from netcad.device import Device, DeviceInterface
from netcad.helpers import range_string

# def j2_filter_vlans_used(
#     obj: t.Union[Device, DeviceInterface], scope="vlans"
# ) -> t.Union[t.List[VlanProfile], VlanProfile]:
#
#     # get the attribute value for the named "scope"
#
#     if not (attr_val := getattr(obj.profile, scope, None)):
#         raise RuntimeError(f"Missing interface profile attribute: {obj.name}: {scope}")
#
#     if isinstance(obj, Device):
#         # return all VLANs used by this devicea
#         # TODO: we could be more specific with different scopes; but for now
#         #       there are not any at the device level.
#         return obj.vlans()
#
#     if isinstance(obj, DeviceInterface):
#         if not isinstance(attr_val, t.Sequence):
#             return attr_val
#
#     return obj.device.vlans() if SENTIAL_ALL_VLANS in attr_val else attr_val


def j2_filter_vlans_id_list(
    if_obj: DeviceInterface
) -> str:
    if not (vlans := getattr(if_obj.profile, 'vlans', None)):
        dev_name = if_obj.device.name
        if_name = if_obj.name
        raise RuntimeError(f"{dev_name}:{if_name} does not have assigned vlans")

    vlans = if_obj.device.vlans() if SENTIAL_ALL_VLANS in vlans else vlans
    return range_string(numbers=[vlan.vlan_id for vlan in vlans])


def j2_filter_vlan_id(
    if_obj: DeviceInterface,
    vlan_attr: str
) -> str:

    vlan: VlanProfile = getattr(if_obj.profile, vlan_attr, None)

    if not vlan:
        dev_name = if_obj.device.name
        if_name = if_obj.name
        raise RuntimeError(f"{dev_name}:{if_name} does not have assigned {vlan_attr}")

    return str(vlan.vlan_id)
