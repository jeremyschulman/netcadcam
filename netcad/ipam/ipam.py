#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import typing as t
from collections import UserDict

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.registry import Registry

from .ipam_network import IPAMNetwork

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["IPAM", "IPAMNetwork"]


class IPAM(Registry, UserDict[t.Hashable, IPAMNetwork]):
    """
    An IPAM instance is a collection of IPNetworkKeeper instances that are
    indexed by the network-keeper "name".  The name is a hashable, typically a
    string value or enum-string.
    """

    def __init__(self, name: t.Hashable):
        """
        Creates an IPAM instance by name and registers that name with the IPAM
        registry.  The IPAM instance can then be used to define further
        networks, and interfaces & hosts therein.

        Parameters
        ----------
        name:
            Any hashable value that can be used as an index into the Registry
            dictionary.
        """
        super().__init__()
        self.name = name
        self.registry_add(name, self)

    def network(self, name: t.Hashable, address: str) -> IPAMNetwork:
        """
        This function creates a new network-keeper instance within the IPAM,
        designated by the name value.  A Caller can retrieve that instance
        using the dict getitem method, for example:

            ipam.network("foo", "10.115.1.0/24")

            ... later ...
            nwk_keeper = ipam["foo"]

        Parameters
        ----------
        name:
            Any hashable value that can be used as a key in the UserDict
            dictionary that underpins the IPAM instance.

        address:
            The IP address network with prefix, for example "192.168.12.0/24".
            The netmask could alternatively be provided, for example:
            "192.168.12.0/255.255.255.0"

        Returns
        -------
        IPAMNetwork instance for the given prefix.
        """
        self[name] = ip_net = IPAMNetwork(self, name, address)
        return ip_net
