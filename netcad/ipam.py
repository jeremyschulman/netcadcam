import typing as t
import ipaddress
from collections import UserDict
from netcad.registry import Registry

IPAMNetworkType = t.Type[t.Union[ipaddress.IPv4Network, ipaddress.IPv6Network]]
IPAMAddressType = t.Type[t.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]]
IPAMInterfaceType = t.Type[t.Union[ipaddress.IPv4Interface, ipaddress.IPv6Interface]]


class IPAMNetwork(UserDict):
    def __init__(self, ipam: "IPAM", prefx: str, gateway=1):
        super(IPAMNetwork, self).__init__()
        self.ipam = ipam
        self.ip_network: IPAMNetworkType = ipaddress.ip_network(address=prefx)
        self._gateway_host_octet: int = gateway

    def interface(self, name, last_octet) -> IPAMInterfaceType:
        """record an IP interface address for the given name"""

        self[name] = ipaddress.ip_interface(
            f"{self.ip_network.network_address + last_octet}/{self.ip_network.netmask}"
        )

        return self[name]

    def host(self, name: t.Hashable, last_octet: int) -> IPAMAddressType:
        """
        Create a host IP address for the given name usig the `last_octet`
        combined with the subnet address.

        Parameters
        ----------
        name: Any
            Used to uniquely identify the name of the host; does not need to be a string but
            must be a hashable value.

        last_octet: int
            The last octet of the IP address

        Returns
        -------
        The ipaddress instance for the IP address.
        """
        self[name] = ipaddress.ip_address(
            f"{self.ip_network.network_address + last_octet}/{self.ip_network.netmask}"
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


class IPAM(Registry):
    def __init__(self, name: str):
        self.name = name
        self.registry_add(name, self)

    def network(self, prefix: str):
        return IPAMNetwork(self, prefix)
