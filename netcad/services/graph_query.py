from operator import attrgetter
from collections import deque
from collections.abc import Iterable

from first import first
import igraph


class GraphQuery:
    target_vertex = attrgetter("target_vertex")
    source_vertex = attrgetter("source_vertex")
    index = attrgetter("index")

    def __init__(self, graph):
        self.graph = graph
        self.nodes: deque[igraph.Vertex] = deque()

    def first(self):
        return first(self.nodes)

    def out_(self, **query):
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

    def in_(self, **query):
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

    def node(self, **query):
        self.nodes = deque(self.graph.vs.select(map(self.index, self.nodes), **query))
        return self

    def __call__(self, start_node: igraph.Vertex | Iterable[igraph.Vertex]):
        self.nodes = (
            deque(start_node)
            if isinstance(start_node, Iterable)
            else deque([start_node])
        )
        return self

    def __len__(self):
        return len(self.nodes)
