#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import typing as t
import ipaddress
from collections import UserDict

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .ip_any import AnyIPInterface, AnyIPNetwork, AnyIPAddress

if t.TYPE_CHECKING:
    from .ipam import IPAM


class IPAMNetwork(UserDict):
    """
    An IPAMNetwork is a collection of IP interfaces, hosts, and even subnets,
    within the given network.

    By default, the gateway IP is the "+1" of the network address. For example,
    if the network address is "192.168.1.0/24", the gateway is
    "192.168.1.1/24".  The `gateway` attribute returns this value as an
    AnyIPInterface instance so that the Caller can use the value either as an
    interface value or by using the `ip` attribute to get the host IP without
    the subnet-prefixlen.

    Attributes
    ----------
    ipam: IPAM - parent IPAM instance

    name: hashable - name associated to the network address

    ip_network: AnyIPNetwork
        An instance of ipaddress.ip_network that stores the network address
        value and properties for the Caller to use.
    """

    def __init__(
        self, ipam: "IPAM", name: t.Hashable, address: str | AnyIPNetwork, gateway=1
    ):
        """
        Constructor for an IPAMNetwork instance.

        Parameters
        ----------
        ipam: IPAM
            The parent owner of this IPAMNetwork, used for backrefering
            purposes.

        name: str
            The designated name of the network.  Typically, this value
            corresponds to the name of the network in an IPAM product, such as
            Netbox | InfoBlox, etc.

        address: str
            The network address with prefix value.  For example
            "192.168.1.0/24".  This value is then converted into an
            AnyIPNetwork instance, stored in the `ip_network` attribute.
        """
        super(IPAMNetwork, self).__init__()
        self.ipam = ipam
        self.name = name
        self.ip_network: AnyIPNetwork = (
            ipaddress.ip_network(address=address)
            if isinstance(address, str)
            else address
        )
        self._gateway_host_octet: int = gateway

    def interface(
        self, name: t.Hashable, last_octet: int, new_prefix: t.Optional[int] = None
    ) -> AnyIPInterface:
        """
        Adds an IP interface instance to the network.  If the given name
        already exists in the network collection, the new IP interface will
        replace it.

        Parameters
        ----------
        name: Hashable
            The value used to identify this interface instance within the
            network collection.  This value is used by the Caller when
            retrieving the interface instance via dict-getitem, for example:

            nwk.interface(name="foo", host_octet=22)

            ... later ...

            iface = nwk["foo"]

        last_octet: int
            The 4th octet value that is added to the network address base to
            formulate the IP interface value.

        new_prefix: int, optional
            When provided, this value is used as the interface prefixlen value.
            By default, the prefixlen value is taken from the network address.
            The new_prefix value is typically used when defining a Loopback
            interface that is designated as a /32.  For example:

                nwk = ipam.network("loopbacks", "192.168.10.0/24")
                sw1_lo0 = nwk.interface("switch1.lo0", 22, new_prefix=32)
                sw2_lo0 = nwk.interface("switch2.lo0", 32, new_prefix=32)

        Returns
        -------
        The AnyIPInterface created.
        """

        self[name] = ipaddress.ip_interface(
            f"{self.ip_network.network_address + last_octet}/{new_prefix or self.ip_network.netmask}"
        )

        return self[name]

    def loopback(self, name: t.Hashable, host_octet: int) -> AnyIPInterface:
        return self.interface(
            name, host_octet, new_prefix=self.ip_network.max_prefixlen
        )

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
    def gateway(self, name: t.Optional[t.Hashable] = "gateway") -> "AnyIPInterface":
        """
        Returns the IP address instance (not interface) of the network gateway
        address.  Registers this instance under the name "gateway".

        Returns
        -------
        IP address instance.
        """
        ip = self.ip_network.network_address + self._gateway_host_octet
        return self.setdefault(
            name, ipaddress.ip_interface((ip, self.ip_network.prefixlen))
        )

    def network(self, name: t.Hashable, prefix: str | AnyIPNetwork) -> "IPAMNetwork":
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
        ip_net = self[name] = IPAMNetwork(self.ipam, name, prefix)
        return ip_net

    def __str__(self):
        return self.ip_network.__str__()
