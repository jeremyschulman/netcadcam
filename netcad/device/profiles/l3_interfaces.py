#  Copyright (c) 2021-2022 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional
from ipaddress import IPv4Interface

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device.profiles.interface_profile import InterfaceVirtual, InterfaceProfile

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "InterfaceL3",
    "InterfaceIsLoopback",
    "InterfaceIsManagement",
    "InterfaceIsInVRF",
]

# -----------------------------------------------------------------------------
#
#                        Interface Profiles for VLANs
#
# -----------------------------------------------------------------------------


class InterfaceL3(InterfaceProfile):
    def __init__(self, if_ipaddr: Optional[IPv4Interface] = None, **params):
        super(InterfaceL3, self).__init__(**params)
        self.if_ipaddr = if_ipaddr


class InterfaceIsManagement(InterfaceL3):
    """
    An interface that is only used for out of band management
    """

    is_mgmt_only = True


class InterfaceIsLoopback(InterfaceVirtual, InterfaceL3):
    """
    A loopback interface is a virtual IP address
    """

    is_loopback = True


class InterfaceIsInVRF(InterfaceL3):
    is_in_vrf = True
    vrf: Optional[str] = "management"
