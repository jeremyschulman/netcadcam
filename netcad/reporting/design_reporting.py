#  Copyright (c) 2022 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List
from typing import TYPE_CHECKING
from collections import defaultdict

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from bidict import bidict
import igraph
from rich.console import Console

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .reporting_typedefs import ResultMapT, NodeObjIDMapT
from .service_reporting import ServiceReporting

if TYPE_CHECKING:
    from netcad.design import Design


class DesginReporting:
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
        self.reporters: List[ServiceReporting] = list()

    def build(self):
        for svc in self.design.services.values():
            self.reporters.append(svc.reporter(drg=self))

        for gr in self.reporters:
            gr.build_graph_nodes()

        for gr in self.reporters:
            gr.build_graph_edges()

    def run_reports(self):
        # TODO: probably move this printing of report tables to the CLI function.
        console = Console()
        for reporter in self.reporters:
            reporter.run_reports()
            if len(reporter.logs):
                console.print(reporter.logs.pretty_table())
