from typing import Optional, TYPE_CHECKING

from pydantic.dataclasses import dataclass, Field

if TYPE_CHECKING:
    from netcad.device import DeviceInterface


@dataclass(frozen=True)
class VlanProfile:
    name: str
    vlan_id: int = Field(..., ge=1, le=4094)
    description: Optional[str] = Field(None)


# declare a sentinal instance to indicate that all VLANs defined on a device
# should be used. this is a common use-case for uplink trunk ports.

SENTIAL_ALL_VLANS = VlanProfile(name="*", vlan_id=1)
VLANS_ALL = [SENTIAL_ALL_VLANS]

# declare a mechanism to indicate that that the profile is using the same value
# as the peer interface.  We will use a technique called a Python descriptor to
# make this associative reference.  A good primer/article on Python descriptors
# can be found here:
# # https://adamj.eu/tech/2021/10/13/how-to-create-a-transparent-attribute-alias-in-python/


class VlanProfileFromPeer:
    def __init__(self):
        self._attr_name = None

    def __set_name__(self, owner, name):
        self._attr_name = name

    def __get__(self, instance, owner):
        # if no instance, then class lookup, return descriptor
        if instance is None:
            return self

        if_active: DeviceInterface = instance.interface
        if not (if_peer := if_active.cable_peer):
            raise RuntimeError(
                f"Unexpected missing interface peer on: {if_active.device_ifname}"
            )

        if not (vlan_prof_attr := getattr(if_peer.profile, self._attr_name, None)):
            raise RuntimeError(
                f"Unexpected missing profile attribute: {self._attr_name} "
                f"on peer interface porfile: {if_peer.device_ifname}"
            )

        if isinstance(vlan_prof_attr, list) and SENTIAL_ALL_VLANS in vlan_prof_attr:
            return if_peer.device.vlans()

        return vlan_prof_attr
