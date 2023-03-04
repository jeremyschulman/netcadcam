# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple
from ipaddress import IPv4Network, IPv4Interface
from collections import UserDict


class P2PInterfaces(UserDict):
    """
    This class provides a dict like instance for taking an IPv4 network and
    returning /31 interface. The two /31 interface IPs that act as the
    point-to-point endpoints.

    The return interface instances are type ipaddress.IPv4Interface

    The default behavior is to use the getitem method with the key set as the
    starting interfacee subnet.

    For example:
        transits = P2PInterfaces("10.115.124.0/24")

        # get the two /31 interface that start at the ".10" subnet
        if_a, if_b = transits[10]

    # if_a = IPv4Interface("10.115.124.10/31")
    # if_b = IPv4Interface("10.115.124.11/31")

    The alternate behavior is to create the P2PInterface with
    `octet_mode=False` and then the getitem key value is the n-th interface.
    For example:

    For example:

        transits = P2PInterfaces("10.115.124.0/24", octet_mode=False)

        # get the 5-th set of /31 interfaces
        if_a, if_b = transits[5]

    # if_a = IPv4Interface("10.115.124.10/31")
    # if_b = IPv4Interface("10.115.124.11/31")
    """

    def __init__(self, network: str, octet_mode=True):
        super().__init__()
        self.network = IPv4Network(network)
        self.octet_mode = octet_mode
        self.new_prefix = 31

    def __missing__(
        self,
        key: int | tuple[int],
    ) -> Tuple[IPv4Interface]:
        """
        Returns a tuple of two IPv4 Interface instances with /31 prefixlen
        whose values are the offset from the network address.  The first is the
        "even" numbered interface and the second is the "odd".

        Parameters
        ----------
        key: int
            Identifies which /31 pair of interfaces to retrieve, as described.
            For example, if the subnet was "192.168.10.0/24" and the key was
            22, then the returned IPs would be IPInterface instances with
            values: (192.168.10.22, 192.168.10.23)

        key: tuple[int]
            When the key is a tuple of integers each value represts the offset
            of that octet in the subnet.  For example if the subnet was
            "192.168.0.0/16" and the key was the tupe (2, 10), then the
            returned IPs would be IPv4Interface instance with values:
            (192.168.2.10/16, 192.168.2.11/16)
        """

        # if the key is not a tuple, then shape it into one.
        is_key_tup = isinstance(key, tuple)

        if not is_key_tup:
            key = (key,)

        if len(key) > 4:
            raise ValueError("Invalid key length, must be <= 4")

        key_offset = sum(
            (256**pow_256) * number for pow_256, number in enumerate(reversed(key))
        )

        netaddr_offset, is_odd = divmod(key_offset, 2)

        p2p_subnet = IPv4Network(
            (self.network.network_address + (netaddr_offset * 2), self.new_prefix)
        )

        if not self.network.supernet_of(p2p_subnet):
            raise ValueError(f"{p2p_subnet} not a subnet of {self.network}")

        p2p_ifs = tuple(
            IPv4Interface((host, p2p_subnet.prefixlen)) for host in p2p_subnet.hosts()
        )

        # save the key-value for future lookups.  if the given key was a tuple,
        # then form the mate-key as a non-tuple.

        if not is_key_tup:
            given_key = key[0]
            mate_key = given_key + (-1 if is_odd else 1)
            self.data[given_key] = self.data[mate_key] = p2p_ifs

        # otherwise, the given key was a tuple, and we need to store the
        # mate-key also as tuple.

        else:
            given_key = list(key)
            self.data[key] = p2p_subnet
            given_key[-1] += -1 if is_odd else 1
            self.data[tuple(given_key)] = p2p_ifs

        return p2p_ifs
