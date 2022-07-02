#  Copyright (c) 2022 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Iterator, TYPE_CHECKING, Optional, Set, List
import json
from pathlib import Path
from itertools import filterfalse

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import igraph

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import netcad_globals
from netcad.device import Device, PseudoDevice, HostDevice
from netcad.checks import CheckCollectionT, CheckResult

if TYPE_CHECKING:
    from netcad.design import DesignService

from .dcrg import DesignCheckResultsGraph


class DesignServiceResultsGraph:
    def __init__(self, drg: DesignCheckResultsGraph, service: "DesignService"):
        self.design = drg.design
        self.service = service
        self.graph = drg.graph
        self.results_map = drg.results_map
        self.nodes_map = drg.nodes_map
        self.nodes: Set[CheckResult] = set()
        self.devices: List[Device] | None = None

    def build_graph_nodes(self):
        """
        This function is used to ingest the check results file payloads (JSON)
        from the persisted files, create the graph node objects and store them
        into the `nodeobj_map` and `result_map` collections.
        """

        self.devices = list(
            filterfalse(
                lambda d: isinstance(d, (HostDevice, PseudoDevice)),
                self.service.devices,
            )
        )

        for check_type in self.service.check_collections:
            for device in self.devices:
                result_objs = self.load_results_files(device, check_type)
                self.add_result_nodes(device, result_objs)

    def build_graph_edges(self):
        """Required by subclass"""
        pass

    def add_result_nodes(self, device: Device, results: Iterator[CheckResult]):
        for res_obj in results:
            check = res_obj.check
            check_type = check.check_type
            node: igraph.Vertex = self.graph.add_vertex(
                kind=check_type, status=res_obj.status, device=res_obj.device
            )
            self.nodes.add(res_obj)
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

        # if the check results file does not exist, then return an empty
        # iterator so the calling scope is AOK.

        results_file = self.device_results_file(device, check_type)
        if not results_file.exists():
            return ()

        # TODO: for now only include the PASS/FAIL status results.  We should
        #       add the INFO nodes to the graph as there could be meaningful
        #       use of these nodes for report processing.

        return (
            check_type.parse_result(res_obj)
            for res_obj in json.load(results_file.open())
            if res_obj["status"] in ("PASS", "FAIL")
        )
