#  Copyright (c) 2022 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Sequence
from typing import TYPE_CHECKING
from collections import defaultdict

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from bidict import bidict
import igraph


# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .drg_typedefs import ResultMapT, NodeObjIDMapT

if TYPE_CHECKING:
    from netcad.design import Design


class DesignResultsGraph:
    """
    DesignResultsGraph stores the graph of all check-results across all the
    design services.  There is one graph.  Each design-service-result graph
    will be initalized with a reference to this graph so that it can populate
    the contents.
    """

    def __init__(self, design: "Design"):
        self.graph = igraph.Graph(directed=True)
        self.design = design
        self.results_map: ResultMapT = defaultdict(lambda: defaultdict(dict))
        self.nodes_map: NodeObjIDMapT = bidict()

    def build(self, services: Optional[Sequence[str]]):

        svcs = self.design.services.values()
        if services:
            svcs = filter(lambda s: s.name in services, svcs)

        svc_graphs = list()
        for svc in svcs:
            svc_graphs.append(svc.results_graph(drg=self))

        for gr in svc_graphs:
            gr.build_graph_nodes()

        for gr in svc_graphs:
            gr.build_graph_edges()
