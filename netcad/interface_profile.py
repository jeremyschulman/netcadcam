# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, List, Set, Type, Sequence, Union
from itertools import chain
from pathlib import Path

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------
import jinja2

from netcad.port_profile import PortProfile
from netcad import vlan_profile as vp
from netcad.device_interface import DeviceInterface

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class InterfaceProfile(object):

    # `template` stores the Jinja2 template text that is used to render the
    # interface specicifc configuration text.

    template: Optional[Union[str, Path]] = None

    # `port_profile` stores the physical layer information that is associated to
    # this interface.

    port_profile: Optional[PortProfile] = None

    # `desc` stores the interface description.  Set as a class value when all
    # instances share the same interface description value.

    desc: Optional[str] = ""

    def __init__(self, **kwargs):
        # the device instance this profile is bound to.  This value is assigned
        # by the DeviceInterface.profile propery

        self.interface: Optional[DeviceInterface] = None

        for attr, value in kwargs.items():
            setattr(self, attr, value)

    def get_template(self, env: jinja2.Environment) -> jinja2.Template:
        if not self.template:
            raise RuntimeError(
                f"Interface profile missing template: {self.__class__.__name__}"
            )

        if isinstance(self.template, Path):
            return env.get_template(str(self.template))

        if isinstance(self.template, str):
            return env.get_template("str:" + self.template)

        raise RuntimeError(
            "Interface profile unexpected template type: "
            f"{self.__class__.__name__}: {type(self.template)}"
        )

    @property
    def name(self):
        return self.__class__.__name__


# -----------------------------------------------------------------------------
#
#                       Layer-2 (VLAN) Interface Profiles
#
# -----------------------------------------------------------------------------


class InterfaceL2(InterfaceProfile):
    def vlans_used(self) -> Set[vp.VlanProfile]:
        raise NotImplementedError()


class InterfaceL2Access(InterfaceL2):
    vlan: vp.VlanProfile

    def vlans_used(self) -> Set[vp.VlanProfile]:
        return {self.vlan}


class InterfaceL2Trunk(InterfaceL2):
    native_vlan: Optional[vp.VlanProfile]
    vlans: List[vp.VlanProfile]

    def vlans_used(self) -> Set[vp.VlanProfile]:
        return set(filter(None, chain([self.native_vlan], self.vlans)))


# -----------------------------------------------------------------------------
#
#                Link Aggregation / Port-Channel Interface Profiles
#
# -----------------------------------------------------------------------------


class InterfaceVirtual(InterfaceProfile):
    is_virtual = True


class InterfaceLagMember(InterfaceProfile):
    def __init__(self, if_lag_parent_profile: InterfaceProfile, **kwargs):
        super(InterfaceLagMember, self).__init__(**kwargs)
        self.if_lag_parent_profile = if_lag_parent_profile
        self.if_parent = kwargs.get("if_parent")


class InterfaceLag(InterfaceVirtual):
    if_lag_member_profile: Optional[Type[InterfaceLagMember]] = InterfaceLagMember
    if_lag_members: List[DeviceInterface] = list()

    def __init__(
        self,
        if_parent: Optional[DeviceInterface] = None,
        if_members: Optional[Sequence[DeviceInterface]] = None,
        **kwargs,
    ):
        super(InterfaceLag, self).__init__(**kwargs)
        self._if_parent: Optional[DeviceInterface] = None

        if if_parent:
            self.lag_parent(if_parent)

        if if_members:
            self.lag_members(*if_members)

    @property
    def lag_number(self):
        return self._if_parent.port_numbers[0]

    def lag_members(self, *if_members: DeviceInterface):
        for if_member in if_members:
            if_member.profile = self.if_lag_member_profile(if_lag_parent_profile=self)
            if_member.profile.if_parent = self.if_parent
            self.if_lag_members.append(if_member)

    def lag_parent(self, if_parent: DeviceInterface):
        self._if_parent = if_parent
        self._if_parent.profile = self

    @property
    def if_parent(self):
        return self._if_parent
