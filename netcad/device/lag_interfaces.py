#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Type, Sequence

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

    def __init__(
        self,
        if_parent: Optional[DeviceInterface] = None,
        if_members: Optional[Sequence[DeviceInterface]] = None,
        **kwargs,
    ):
        super(InterfaceLag, self).__init__(**kwargs)

        self._if_parent: Optional[DeviceInterface] = None
        self.if_lag_members = list()

        if if_parent:
            self.lag_parent = if_parent

        if if_members:
            self.add_lag_members(*if_members)

    @property
    def lag_number(self):
        return self.lag_parent.port_numbers[0]

    @property
    def lag_parent(self) -> DeviceInterface:
        """
        Returns the interface bound to this LAG profile.  The interface
        "Port-Channel2000" for example, would be the lag_parent of the Lag
        profile.
        """
        return self._if_parent or self.interface

    @lag_parent.setter
    def lag_parent(self, if_parent: DeviceInterface):
        self._if_parent = if_parent
        self._if_parent.profile = self

    def add_lag_members(self, *if_members: DeviceInterface):
        for if_member in if_members:
            if_member.profile = self.if_lag_member_profile(if_lag_parent_profile=self)
            if_member.profile.if_parent = self.lag_parent
            self.if_lag_members.append(if_member)
