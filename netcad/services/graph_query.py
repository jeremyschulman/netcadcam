#  Copyright (c) 2025 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from operator import attrgetter
from collections import deque

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from first import first
import igraph

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ['GraphQuery']

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class GraphQuery:
    """
    A class to query an igraph graph using a very simplified gremlin inspired
    syntax.
    """

    target_vertex = attrgetter("target_vertex")
    source_vertex = attrgetter("source_vertex")
    index = attrgetter("index")

    def __init__(self, graph):
        self.graph = graph
        self.nodes: deque[igraph.Vertex] = deque()

    def first(self) -> igraph.Vertex | None:
        """returns the first node in the current set of nodes, or None"""
        return first(self.nodes)

    def out_(self, **query) -> "GraphQuery":
        """
        Query the current set of graph nodes that are connected to the current
        nodes by an outgoing edge that matches the query.
        """
        found_nodes = deque()
        while True:
            try:
                node = self.nodes.popleft()
            except IndexError:
                break

            found_nodes.extend(
                map(
                    self.target_vertex,
                    self.graph.es.select(map(self.index, node.out_edges()), **query),
                )
            )

        self.nodes = found_nodes
        return self

    def in_(self, **query) -> "GraphQuery":
        """
        Query the current set of graph nodes that are connected to the current
        nodes by an incoming edge that matches the query.
        """
        found_nodes = deque()
        while True:
            try:
                node = self.nodes.popleft()
            except IndexError:
                break

            found_nodes.extend(
                map(
                    self.source_vertex,
                    self.graph.es.select(map(self.index, node.in_edges()), **query),
                )
            )

        self.nodes = found_nodes
        return self

    def node(self, **query) -> "GraphQuery":
        """
        Query the current set of nodes that match the query.
        """
        self.nodes = deque(self.graph.vs.select(map(self.index, self.nodes), **query))
        return self

    def __call__(self, *start_nodes: igraph.Vertex):
        """
        Set the starting nodes for the query.
        """
        self.nodes = deque(start_nodes)
        return self

    def __len__(self):
        """
        Get the number of nodes in the current set of nodes.
        """
        return len(self.nodes)
