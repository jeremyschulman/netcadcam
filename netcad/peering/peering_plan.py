#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Set, DefaultDict, TypeVar, Generic, Dict, Hashable
from collections import defaultdict

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .peering_types import Peer, PeeringID, PeeringEndpoint

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["PeeringPlanner"]

PP = TypeVar("PP", bound=Peer)
PE = TypeVar("PE", bound=PeeringEndpoint)


class PeeringPlanner(Generic[PP, PE]):
    """
    Corresponds to a Graph that maintains the relationship of Peer and
    PeeringEndpoints instances.

    Attributes
    ----------
    peers: dict
        The unique set of peers managed by a PeeringPlanner instance. The key
        is the peer name, as defined by the concrete type of the planning peer
        (PP)

    edges: DefaultDict[Hashable, set[E]]
        A dictionary whose key=peering-ID and value is the set of endpoings
        associated with that peering-ID

    validated: bool
        True if the peering planner instance has been build-validated.
    """

    def __init__(self, name: str):
        self.name = name
        self.peers: Dict[Hashable, PP] = dict()
        self.edges: DefaultDict[PeeringID, Set[PE]] = defaultdict(set)
        self.validated = False

    def get_peer(self, name: Hashable) -> PP:
        return self.peers.get(name)

    def add_peers(self, *peers: PP):
        for peer in peers:
            self.peers[peer.name] = peer

    def _add_endpoint(self, peering_id: PeeringID, peer_endpoint: PE):
        self.edges[peering_id].add(peer_endpoint)
        self.validated = False

    def _check_endpoints_enabled(self):
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

    def validate(self):
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

        for peering_id, peering_endpoints in self.edges.items():
            edges_by_counts[len(peering_endpoints)].append(
                {peering_id: peering_endpoints}
            )

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

        self._check_endpoints_enabled()

        # if here, then everying is AOK from a validation point of view.

        self.validated = True

    def build(self):
        """
        The build function is used to connect the peering_endpoints to each
        other via the PeerEndpoint.peer_endpoint attribute
        """

        endpoint: PE
        for peer in self.peers.values():
            for endpoint in peer.endpoints:
                self.edges[endpoint.peer_id].add(endpoint)

        self.validate()

        # link each endpoint to each other
        # TODO: figure out why PyCharm cannot typehint the return of
        #       edges.values()
        end_a: PE
        end_b: PE
        for end_a, end_b in self.edges.values():
            end_a.remote = end_b
            end_b.remote = end_a
