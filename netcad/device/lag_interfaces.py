# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, List, Type, Sequence

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device.device_interface import DeviceInterface
from .interface_profile import InterfaceProfile, InterfaceVirtual

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["InterfaceLag", "InterfaceLagMember"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


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
            self.lag_parent = if_parent

        if if_members:
            self.add_lag_members(*if_members)

    @property
    def lag_number(self):
        return self._if_parent.port_numbers[0]

    @property
    def lag_parent(self) -> DeviceInterface:
        """
        Returns the interface bound to this LAG profile.  The interface
        "Port-Channel2000" for example, would be the lag_parent of the Lag
        profile.
        """
        return self._if_parent

    @lag_parent.setter
    def lag_parent(self, if_parent: DeviceInterface):
        self._if_parent = if_parent
        self._if_parent.profile = self

    def add_lag_members(self, *if_members: DeviceInterface):
        for if_member in if_members:
            if_member.profile = self.if_lag_member_profile(if_lag_parent_profile=self)
            if_member.profile.if_parent = self.lag_parent
            self.if_lag_members.append(if_member)

    # def set_lag_parent(self, if_parent: DeviceInterface):
    #     self._if_parent = if_parent
    #     self._if_parent.profile = self

    # @property
    # def if_parent(self):
    #     return self._if_parent
