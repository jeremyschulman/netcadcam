#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Set, Optional, List

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device.profiles.interface_profile import InterfaceProfile
from ..vlan_profile import VlanProfile, VlanProfileRegistry

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

    @staticmethod
    def fields_from_decl(ifp_decl: dict):
        if not (vlan_name := ifp_decl.get("vlan")):
            return {}

        if not (vlan_obj := VlanProfileRegistry.get(vlan_name)):
            raise ValueError(f"vlan profile '{ifp_decl['vlan']}' not found")

        return {"vlan": vlan_obj}


class InterfaceL2Trunk(InterfaceL2):
    native_vlan: Optional[VlanProfile]
    allowed_vlans: List[VlanProfile]

    def vlans_used(self) -> Set[VlanProfile]:
        """
        Return the set of all vlans used by this interface, inclusive of the
        native vlan, if defined.
        """
        native = {self.native_vlan} if hasattr(self, "native_vlan") else set()
        return set(self.allowed_vlans) | native

    def trunk_allowed_vlans(self) -> Set[VlanProfile]:
        """
        Returns the set of vlans that should be included in a vlan trun allowed
        type statement.  This set of vlans will also be used when correlating
        this interface to the vlans for which it is assgined.  By default, the
        allowed vlans is the used vlans minus the native vlan.

        A Designer may wish to include the native vlan on the allowed vlans
        list, even though this is considered a security risk / not a best
        practice.  In these cases, the Designer must overload this method in the
        subclass profile definition.
        """
        # native = set(getattr(self, "native_vlan", None))
        return set(self.allowed_vlans)

    @staticmethod
    def fields_from_decl(ifp_decl: dict):
        ret = dict()

        if alwd := ifp_decl.get("allowed_vlans"):
            ret["allowed_vlans"] = [
                VlanProfileRegistry.get(vlan_name) for vlan_name in alwd
            ]

        if nvn := ifp_decl.get("native_vlan"):
            ret["native_vlan"] = VlanProfileRegistry[nvn]

        return ret
