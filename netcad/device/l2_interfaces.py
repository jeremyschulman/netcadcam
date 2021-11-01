# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Set, Optional, List
from itertools import chain

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .interface_profile import InterfaceProfile
from netcad.vlan import VlanProfile

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["InterfaceL2", "InterfaceL2Access", "InterfaceL2Trunk", "VlanProfile"]

# -----------------------------------------------------------------------------
#
#                       Layer-2 (VLAN) Interface Profiles
#
# -----------------------------------------------------------------------------


class InterfaceL2(InterfaceProfile):
    def vlans_used(self) -> Set[VlanProfile]:
        raise NotImplementedError()


class InterfaceL2Access(InterfaceL2):
    vlan: VlanProfile

    def vlans_used(self) -> Set[VlanProfile]:
        return {self.vlan}


class InterfaceL2Trunk(InterfaceL2):
    native_vlan: Optional[VlanProfile]
    vlans: List[VlanProfile]

    def vlans_used(self) -> Set[VlanProfile]:
        return set(
            filter(None, chain([getattr(self, "native_vlan", None)], self.vlans))
        )
