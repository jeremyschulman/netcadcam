# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List
from ipaddress import IPv4Network, IPv4Interface
from collections import UserDict
from itertools import islice


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

    def __missing__(self, key: int) -> List[IPv4Interface]:
        """
        Returns a list of two IPv4 Interface instances with /31 prefixlen. The
        first is the "even" numbered interface and the second is the "odd".

        Parameters
        ----------
        key: int
            Identifies which /31 pair of interfaces to retrieve, as described.

        Returns
        -------
        list as described
        """

        index, rem = divmod(key, 2) if self.octet_mode else (key, 0)

        search = islice(self.network.subnets(new_prefix=31), index, index + 1)

        if not (net := next(search)):
            raise RuntimeError(f"{key} not found in {self.network}")

        return [IPv4Interface((host, net.prefixlen)) for host in net.hosts()]
