#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Set

from netcad.device.profiles.interface_profile import InterfaceVirtual
from netcad.device.profiles.l3_interfaces import InterfaceL3

from ..vlan_profile import VlanProfile


class InterfaceVlan(InterfaceVirtual, InterfaceL3):
    """
    InterfaceVlan is used to declare IP addresses assigned to VLANs.  Also
    referred to an SVI.
    """

    vlan: VlanProfile

    def vlans_used(self) -> Set[VlanProfile]:
        return {self.vlan}
