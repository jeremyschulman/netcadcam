#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import typing as t
import ipaddress
from collections import UserDict
from netcad.registry import Registry

AnyIPNetwork = t.Union[ipaddress.IPv4Network, ipaddress.IPv6Network]
AnyIPAddress = t.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]
AnyIPInterface = t.Union[ipaddress.IPv4Interface, ipaddress.IPv6Interface]


class IPAMNetworkKeeper(UserDict):
    def __init__(self, ipam: "IPAM", name: t.Hashable, prefx: str, gateway=1):
        super(IPAMNetworkKeeper, self).__init__()
        self.ipam = ipam
        self.name = name
        self.ip_network: AnyIPNetwork = ipaddress.ip_network(address=prefx)
        self._gateway_host_octet: int = gateway

    def interface(self, name: str, host_octet: int, new_prefix=None) -> AnyIPInterface:
        """record an IP interface address for the given name"""

        self[name] = ipaddress.ip_interface(
            f"{self.ip_network.network_address + host_octet}/{new_prefix or self.ip_network.netmask}"
        )

        return self[name]

    def host(self, name: t.Hashable, offset_octet: int) -> AnyIPAddress:
        """
        Create a host IP address for the given name usig the `last_octet`
        combined with the subnet address.

        Parameters
        ----------
        name: Any
            Used to uniquely identify the name of the host; does not need to be a string but
            must be a hashable value.

        offset_octet: int
            The last octet of the IP address

        Returns
        -------
        The ipaddress instance for the IP address.
        """
        self[name] = ipaddress.ip_address(
            f"{self.ip_network.network_address + offset_octet}"
        )

        return self[name]

    @property
    def gateway(self) -> "AnyIPInterface":
        """
        Returns the IP address instance (not interface) of the network gateway
        address.  Registers this instance under the name "gateway".

        Returns
        -------
        IP address instance.
        """
        ip = self.ip_network.network_address + self._gateway_host_octet
        return self.setdefault(
            "gateway", ipaddress.ip_interface((ip, self.ip_network.prefixlen))
        )

    def network(self, name: t.Hashable, prefix: str) -> "IPAMNetworkKeeper":
        """
        This function creates a new network instance within the IPAM,
        designated by the name value.  This network can then be retrieved using
        "getitem" via the designated name.

        Parameters
        ----------
        name:
            Any hashable value that can be used as a key in the UserDict
            dictionary that underpins the IPAM instance.

        prefix:
            The IP address network with prefix, for example "192.168.12.0/24".
            The netmask could alternatively be provided, for example:
            "192.168.12.0/255.255.255.0"

        Returns
        -------
        IPAMNetwork instance for the given prefix.
        """
        ip_net = self[name] = IPAMNetworkKeeper(self.ipam, name, prefix)
        return ip_net

    def __str__(self):
        return self.ip_network.__str__()


class IPAM(Registry, UserDict[t.Hashable, IPAMNetworkKeeper]):
    """
    The IPAM class is used to store instances of dictionary like object that
    whose keys can be any hashable item, such as a string-name, or VlanProfile,
    and whose values are instance of the IPAMNetwork class.
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

    def network(self, name: t.Hashable, address: str) -> IPAMNetworkKeeper:
        """
        This function creates a new network instance within the IPAM,
        designated by the name value.  This network can then be retrieved using
        "getitem" via the designated name.

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
        self[name] = ip_net = IPAMNetworkKeeper(self, name, address)
        return ip_net
