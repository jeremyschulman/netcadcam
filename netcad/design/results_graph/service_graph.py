# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Iterator, TYPE_CHECKING, Optional
import json
from collections import defaultdict
from pathlib import Path

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from bidict import bidict
import igraph


# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import netcad_globals
from netcad.device import Device
from netcad.checks import CheckCollectionT, CheckResult
from .drg_typedefs import ResultMapT, NodeObjIDMapT

if TYPE_CHECKING:
    from netcad.design import DesignService


class DesignServiceResultsGraph:
    def __init__(self, service: "DesignService"):
        self.service = service
        self.graph = igraph.Graph(directed=True)
        self.results_map: ResultMapT = defaultdict(lambda: defaultdict(dict))
        self.nodes_map: NodeObjIDMapT = bidict()

    def build_graph_nodes(self):
        """
        This function is used to ingest the check results file payloads (JSON)
        from the persisted files, create the graph node objects and store them
        into the `nodeobj_map` and `result_map` collections.
        """

        for check_type in self.service.check_collections:
            for device in self.service.devices:
                result_objs = self.load_results_files(device, check_type)
                self.add_result_nodes(device, result_objs)

    def build_graph_edges(self):
        """Required by subclass"""
        raise NotImplementedError()

    def add_result_nodes(self, device: Device, results: Iterator[CheckResult]):
        for res_obj in results:
            check = res_obj.check
            check_type = check.check_type
            node: igraph.Vertex = self.graph.add_vertex(kind=check_type)
            self.nodes_map[res_obj] = node.index
            self.results_map[device][check_type][check.check_id()] = res_obj

    # ---------------------------------------------------------------------

    @staticmethod
    def default_edge_kind(source, target):
        f_ct = source.check.check_type
        t_ct = target.check.check_type
        return f"checked,{f_ct},{t_ct}"

    def graph_edge(self, source, target, kind: Optional[str] = None, **attrs):
        source_id = self.nodes_map[source]
        target_id = self.nodes_map[target]
        kind = kind or self.default_edge_kind(source, target)
        self.graph.add_edge(source_id, target_id, kind=kind, **attrs)

    # ---------------------------------------------------------------------

    @staticmethod
    def device_results_file(device: Device, check_type: CheckCollectionT) -> Path:
        check_name = check_type.get_name()
        base_dir = netcad_globals.g_netcad_checks_dir
        return base_dir / device.name / "results" / f"{check_name}.json"

    def load_results_files(
        self, device: Device, check_type: CheckCollectionT
    ) -> Iterator[CheckResult]:
        return map(
            check_type.parse_result,
            json.load(self.device_results_file(device, check_type).open()),
        )
