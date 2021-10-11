# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, List, Set, Type
from itertools import chain


# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.port_profile import PortProfile
from netcad.vlan_profile import VlanProfile
from netcad.device_interface import DeviceInterface

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class InterfaceProfile(object):

    # `template` stores the Jinja2 template text that is used to render the
    # interface specicifc configuration text.

    template: Optional[str] = None

    # `port_profile` stores the physical layer information that is associated to
    # this interface.

    port_profile: Optional[PortProfile] = None

    # `desc` stores the interface description.  Set as a class value when all
    # instances share the same interface description value.

    desc: Optional[str] = ""

    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)


class InterfaceL2Access(InterfaceProfile):
    vlan: VlanProfile

    def if_vlans(self) -> Set[VlanProfile]:
        return {self.vlan}


class InterfaceL2Trunk(InterfaceProfile):
    native_vlan: Optional[VlanProfile]
    vlans: List[VlanProfile]

    def if_vlans(self) -> Set[VlanProfile]:
        return set(filter(None, chain([self.native_vlan], self.vlans)))


class InterfaceLagMember(InterfaceProfile):
    def __init__(self, if_lag_parent_profile: InterfaceProfile, **kwargs):
        super(InterfaceLagMember, self).__init__(**kwargs)
        self.if_lag_parent_profile = if_lag_parent_profile
        self.if_parent = kwargs.get("if_parent")


class InterfaceLag(InterfaceProfile):
    if_lag_member_profile: Optional[Type[InterfaceLagMember]] = InterfaceLagMember
    if_lag_members: List[DeviceInterface] = list()

    def __init__(self, **kwargs):
        super(InterfaceLag, self).__init__(**kwargs)
        self._if_parent = None

    def lag_member(self, if_member: DeviceInterface):
        if_member.profile = self.if_lag_member_profile(if_lag_parent_profile=self)
        if_member.profile.if_parent = self.if_parent
        self.if_lag_members.append(if_member)

    @property
    def if_parent(self):
        return self._if_parent

    @if_parent.setter
    def if_parent(self, has_parent: DeviceInterface):
        self._if_parent = has_parent
        has_parent.profile = self
