#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from netcad.device import DeviceInterface

# declare a mechanism to indicate that the profile is using the same value as
# the peer interface.  We will use a technique called a Python descriptor to
# make this associative reference.
#
# A good primer/article on Python descriptors can be found here:
# # https://adamj.eu/tech/2021/10/13/how-to-create-a-transparent-attribute-alias-in-python/


class VlansFromPeer:
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
                f"Unexpected missing interface peer on: {if_active.device_ifname}, "
                f"cable: {if_active.cable_id}"
            )

        if not (vlan_prof_attr := getattr(if_peer.profile, self._attr_name, None)):
            raise RuntimeError(
                f"Unexpected missing profile attribute: {self._attr_name} "
                f"on peer interface porfile: {if_peer.device_ifname}"
            )

        # TODO: moving to descriptor approach, the val_prof_attr "getter" should
        #       do the right thing here. :fingerscrossed:
        # if isinstance(vlan_prof_attr, list) and SENTIAL_ALL_VLANS in vlan_prof_attr:
        #     return if_peer.device.vlans()

        return vlan_prof_attr
