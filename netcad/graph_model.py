from itertools import chain

from netcad.arango.db import ArangoDatabase
from netcad.arango.consts import CollectionTypes


class GraphModel(object):

    nodes = ["Device", "Port", "Cable"]
    edges = [("Device", "equip_port", "Port"), ("Port", "is_cabled_to", "Cable")]

    def __init__(self, name: str, db: ArangoDatabase):
        self.name = name
        self.db = db
        self.graph = None

    async def ensure(self):
        c_nodes = [self.db.collection(_name) for _name in self.nodes]

        c_edges = [
            self.db.collection(_name, type=CollectionTypes.edge)
            for _from, _name, _to in self.edges
        ]

        # ensure the document and edge collections exist before ensuring the
        # graph.

        for each_col in chain(c_nodes, c_edges):
            await each_col.ensure()

        # ensure the graph instance exists.

        self.graph = self.db.graph(
            name=self.name,
            edgeDefinitions=[
                {"collection": _edge, "from": [_from], "to": [_to]}
                for _from, _edge, _to in self.edges
            ],
        )

        await self.graph.ensure()
