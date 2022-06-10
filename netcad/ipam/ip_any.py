#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import typing as t
import ipaddress

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------


AnyIPNetwork = t.Union[ipaddress.IPv4Network, ipaddress.IPv6Network]
AnyIPAddress = t.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]
AnyIPInterface = t.Union[ipaddress.IPv4Interface, ipaddress.IPv6Interface]

__all__ = ["AnyIPAddress", "AnyIPInterface", "AnyIPNetwork"]
