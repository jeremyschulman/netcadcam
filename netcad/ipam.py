import typing as t
import ipaddress
from collections import UserDict
from netcad.registry import Registry

AnyIPNetwork = t.Union[ipaddress.IPv4Network, ipaddress.IPv6Network]
AnyIPAddress = t.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]
AnyIPInterface = t.Union[ipaddress.IPv4Interface, ipaddress.IPv6Interface]


class IPAMNetwork(UserDict):
    def __init__(self, ipam: "IPAM", name: t.Hashable, prefx: str, gateway=1):
        super(IPAMNetwork, self).__init__()
        self.ipam = ipam
        self.name = name
        self.ip_network: AnyIPNetwork = ipaddress.ip_network(address=prefx)
        self._gateway_host_octet: int = gateway

    def gateway_interface(self, name) -> AnyIPInterface:
        return self.interface(name=name, offset_octet=self._gateway_host_octet)

    def interface(self, name, offset_octet) -> AnyIPInterface:
        """record an IP interface address for the given name"""

        self[name] = ipaddress.ip_interface(
            f"{self.ip_network.network_address + offset_octet}/{self.ip_network.netmask}"
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
    def gateway(self):
        """
        Returns the IP address instance (not interface) of the network gateway
        address.  Registers this instance under the name "gateway".

        Returns
        -------
        IP address instance.
        """
        return self.setdefault(
            "gateway", self.ip_network.network_address + self._gateway_host_octet
        )

    def network(self, name: t.Hashable, prefix: str) -> "IPAMNetwork":
        """
        This function creates an new network instance within the IPAM,
        designated by the name value.  This network can then be retrieve using
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
        ip_net = self[name] = IPAMNetwork(self.ipam, name, prefix)
        return ip_net


class IPAM(Registry, UserDict, t.MutableMapping[t.Hashable, IPAMNetwork]):
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

    def network(self, name: t.Hashable, prefix: str) -> IPAMNetwork:
        """
        This function creates an new network instance within the IPAM,
        designated by the name value.  This network can then be retrieve using
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
        self[name] = ip_net = IPAMNetwork(self, name, prefix)
        return ip_net
