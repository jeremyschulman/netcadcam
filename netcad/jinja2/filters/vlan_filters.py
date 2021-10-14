# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Union, Set, List

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.vlan_profile import VlanProfile, SENTIAL_ALL_VLANS
from netcad.device import DeviceInterface, Device
from netcad.helpers import range_string


def j2_filter_vlans(obj: Union[Device, DeviceInterface], *scopes, **kwargs) -> str:

    if not isinstance(obj, (Device, DeviceInterface)):
        raise RuntimeError(f"Unexpected object type pass to vlans filter: {type(obj)}")

    # -------------------------------------------------------------------------
    # If this is a Device instance, then return all of the VLANs used in a range
    # string format.
    # -------------------------------------------------------------------------

    if isinstance(obj, Device):
        # TODO: we could be more specific with different scopes; but for now
        #       there are not any at the device level.
        return range_string(numbers=[vlan.vlan_id for vlan in obj.vlans()])

    # -------------------------------------------------------------------------
    # DeviceInterface instance.
    # -------------------------------------------------------------------------

    dev_obj: Device = obj.device

    if not scopes:
        scopes = ("vlans",)

    if_vlans: Set[VlanProfile] = set()

    for each_scope in scopes:

        # The scoped attribute could either be a signle VLAN or a list of VLANs
        prof_vlan_attr: Union[VlanProfile, List[VlanProfile]]

        if not (prof_vlan_attr := getattr(obj.profile, each_scope, None)):
            raise RuntimeError(
                f"Missing interface profile attribute: {obj.name}: {each_scope}"
            )

        # if it is a single VLAN, then add it to the list of scopes and check
        # for the next scope

        if not isinstance(prof_vlan_attr, list):
            if_vlans.add(prof_vlan_attr)
            continue

        # The scoped attribute is a list of VLANs ...
        # if the VlanProfile is designed as "all vlans", the return the range
        # string of all VLANs on the device associated to the interface

        if SENTIAL_ALL_VLANS in prof_vlan_attr:
            return range_string(numbers=[vlan.vlan_id for vlan in dev_obj.vlans()])

        if_vlans.update(prof_vlan_attr)

    # if there is only one VLAN to return, then return that string value now.

    if len(if_vlans) == 1:
        return str(if_vlans.pop().vlan_id)

    # if there are more than one VLAN, then return the string, handling the case
    # for VLAN ranges.

    return range_string(
        numbers=[vlan.vlan_id for vlan in sorted(if_vlans, key=lambda _v: _v.vlan_id)]
    )


def j2_filter_vlans_id_list(if_obj: DeviceInterface) -> str:
    if not (vlans := getattr(if_obj.profile, "vlans", None)):
        dev_name = if_obj.device.name
        if_name = if_obj.name
        raise RuntimeError(f"{dev_name}:{if_name} does not have assigned vlans")

    vlans = if_obj.device.vlans() if SENTIAL_ALL_VLANS in vlans else vlans
    return range_string(numbers=[vlan.vlan_id for vlan in vlans])


def j2_filter_vlan_id(if_obj: DeviceInterface, vlan_attr: str) -> str:

    vlan: VlanProfile = getattr(if_obj.profile, vlan_attr, None)

    if not vlan:
        dev_name = if_obj.device.name
        if_name = if_obj.name
        raise RuntimeError(f"{dev_name}:{if_name} does not have assigned {vlan_attr}")

    return str(vlan.vlan_id)
