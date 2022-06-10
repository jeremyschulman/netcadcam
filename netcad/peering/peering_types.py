#  Copyright (c) 2022 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Hashable, TypeVar, Generic, Set


# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["Peer", "PeeringEndpoint", "PeeringID"]

PeeringID = Hashable

P = TypeVar("P")
E = TypeVar("E")


class PeeringEndpoint(Generic[P, E]):
    """Corresponds to a Graph Edge"""

    # unique ID for connecting peering endpoints
    peer_id: PeeringID

    # backreference to the Peer instance that "owns" this endpoint.
    peer: P

    # for "administrative control" if the edge should be actively enabled in
    # the design (think BGP negibhor session).
    enabled: bool

    # remote peering endpoint assigned during the 'build' process
    remote: E

    def __repr__(self):
        return self.__dict__.__repr__()


class Peer(Generic[P, E]):
    """
    A Peer class represents the owner of many endpoint instances.  Each
    endpoint instance is maintained in the Peer collection (set).
    """

    def __init__(self, name: P):
        self.name = name
        self._endpoints: Set[E] = set()

    @property
    def endpoints(self) -> Set[E]:
        return self._endpoints

    def add_endpoint(self, peer_id: PeeringID, endpoint: E):
        endpoint.peer = self
        endpoint.peer_id = peer_id
        self._endpoints.add(endpoint)
