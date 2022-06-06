#  Copyright (c) 2022 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Hashable, TypeVar, Generic, Dict
from dataclasses import dataclass

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

    # assigned during the 'build' process
    peer_endpoint: E


class Peer(Generic[P, E]):
    """Corresponds to a Graph Vertex"""

    def __init__(self, name: P):
        self.name = name
        self._endpoints: Dict[PeeringID, E] = dict()

    @property
    def endpoints(self) -> Dict[PeeringID, E]:
        return self._endpoints

    def add_endpoint(self, peer_id: PeeringID, endpoint: PeeringEndpoint):
        endpoint.peer = self
        endpoint.peer_id = peer_id
        self._endpoints[peer_id] = endpoint
