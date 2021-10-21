# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Set
from ipaddress import IPv4Address

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.vlan import vlan_profile as vp
from netcad.vlan.vlan_profile import VlanProfile
from .interface_profile import InterfaceVirtual

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["InterfaceVlan"]

# -----------------------------------------------------------------------------
#
#                        Interface Profiles for VLANs
#
# -----------------------------------------------------------------------------


class InterfaceLoopback(InterfaceVirtual):
    """
    A loopback interface is a virtual IP address
    """

    is_loopback = True

    def __init__(self, ipaddress: Optional[IPv4Address] = None, **params):
        super(InterfaceLoopback, self).__init__(**params)
        self.ipaddress = ipaddress


class InterfaceVlan(InterfaceVirtual):
    """
    InterfaceVlan is used to declare IP addresses assigned to VLANs.  Also
    referred to an SVI.
    """

    vlan: VlanProfile

    def __init__(self, ipaddress: Optional[IPv4Address] = None, **params):
        super(InterfaceVlan, self).__init__(**params)
        self.ipaddress = ipaddress

    def vlans_used(self) -> Set[vp.VlanProfile]:
        return {self.vlan}
