#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import dataclasses
from typing import Dict, Hashable, Set, Any
from collections import defaultdict

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["PeeringPlanner", "Peer", "PeeringEndpoint", "PeeringID"]


class Peer:
    def __init__(self, name: Any):
        self.name = name


@dataclasses.dataclass(frozen=True)
class PeeringEndpoint:
    peer: Peer
    enabled: bool


PeeringID = Hashable


class PeeringPlanner:
    """
    Attributes
    ----------
    peers: Set[Peer]
        The unique set of peers managed by a PeeringPlanner instance.

    edges: Dict[Hashable, set]
        A dictionary whose key=peering-ID and value is the set of endpoings
        associated with that peering-ID

    validated: bool
        True if the peering planner instance has been build-validated.
    """

    def __init__(self, name: str):
        self.name = name
        self.peers: Set[Peer] = set()
        self.edges: Dict[PeeringID, Set[PeeringEndpoint]] = defaultdict(set)
        self.validated = False

    def add_peers(self, *peers):
        self.peers.update(*peers)

    def add_endpoint(self, peering_id: PeeringID, peer_endpoint: PeeringEndpoint):
        self.edges[peering_id].add(peer_endpoint)
        self.peers.add(peer_endpoint.peer)
        self.validated = False

    def check_endpoints_enabled(self):
        """
        This routine validates that, for each cable, all the endpoints
        associated with a peering-ID has a matching enabled setting, and a
        matching interface speed setting.

        Raises
        ------
        RuntimeErrror - when both endpoints of a peering do not have matching
                        enabled attribute value.
        """

        def edge_list_info():
            return ", ".join(
                [
                    "{}:{} {}".format(
                        edge.peer.name,
                        peer_id,
                        "enabled" if edge.enabled else "disabled",
                    )
                    for edge in edge_endpoints
                ]
            )

        for peer_id, edge_endpoints in self.edges.items():
            if len(set(ep.enabled for ep in edge_endpoints)) != 1:
                raise RuntimeError(
                    f"Not all peer-endpoints in peer-id {peer_id} are set "
                    f"to the same enabled value: {edge_list_info()}"
                )

    def build(self):
        """
        Validates the peering plan by ensureing that each peer contains exactly
        two peer endpoint instances.  If the plan is valid, then the
        `validated` attribute will be set to True.

        If there are no validate peers, meaning, no edges with two end-points,
        then an exception is raised.

        If there are edges with peer-endpooint count != 2, then an exception is
        raised.

        Returns
        -------
        The number of peer edges.
        """

        edges_by_counts = defaultdict(list)

        for peering_id, peering_edges in self.edges.items():
            edges_by_counts[len(peering_edges)].append({peering_id: peering_edges})

        # in a valid scenario, ok_edges is all the edges, and the
        # edges_by_count variable should be empty.

        ok_edges = edges_by_counts.pop(2, None)

        # if there are edges_by_counts remaining it means there are peering-IDs
        # that have a peering count 0, 1, or > 2.

        if edges_by_counts:
            from pprint import pformat

            content = pformat(dict(edges_by_counts), indent=3)
            raise RuntimeError(
                f"Peering plan: {self.name}: Improper peer counts:\n{content}",
            )

        elif not ok_edges:
            raise RuntimeError("No cabling", self, edges_by_counts)

        # if here, then all edges have two endpoints.  We next need to validate
        # that both endpoints are in the same enabled state, either both
        # ennable or both dsiabled.  If an error exists, the call to check
        # below will raise an exception.

        self.check_endpoints_enabled()

        # if here, then everying is AOK from a validation point of view.

        self.validated = True
