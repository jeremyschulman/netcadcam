#  Copyright (c) 2022 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List
from ipaddress import IPv4Network, IPv4Interface
from collections import UserDict
from itertools import islice

__all__ = ["P2PInterfaces"]


class P2PInterfaces(UserDict):
    """
    This class provides a dict like instance for taking an IPv4 network and
    chopping it up in /31 subnets so that each /31 can provide two /31
    interface IPs that act as the point-to-point endpoints.  The Caller can
    then use the instance to obtain the two IPv4 interface endpoints using the
    dict getitem, the key being the /31 starting octet.

    The return interface instances are type ipaddress.IPv4Interface

    For example:
        transits = P2PInterfaces("10.115.124.0/24")

        if_a, if_b = transits[10]

    # if_a = IPv4Interface("10.115.124.10/31")
    # if_b = IPv4Interface("10.115.124.11/31")


    """

    def __init__(self, network: str):
        super().__init__()
        self.network = IPv4Network(network)

    def __missing__(self, key: int) -> List[IPv4Interface]:
        index, rem = divmod(key, 2)
        if rem:
            raise ValueError(f"key {key} is not even")

        search = islice(self.network.subnets(new_prefix=31), index, index + 1)

        if not (net := next(search)):
            raise RuntimeError(f"{key} not found in {self.network}")

        return [IPv4Interface((host, net.prefixlen)) for host in net.hosts()]
