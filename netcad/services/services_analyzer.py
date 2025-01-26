#  Copyright (c) 2025 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import TYPE_CHECKING, Iterator
from collections import defaultdict
import json
from pathlib import Path

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from bidict import bidict
import igraph
from rich.console import Console

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from ..config import netcad_globals
from ..checks import CheckCollectionT, CheckResult

if TYPE_CHECKING:
    from netcad.device import Device
    from netcad.design import Design, DesignFeature

from .design_service import DesignService
from .services_typedefs import ResultMapT, NodeObjIDMapT


class ServicesAnalyzer:
    def __init__(self, design: "Design"):
        self.design = design

        # initalize the top level status to pass.  Could be set to FAIL if any
        # managed service status is "FAIL".
        # TODO: migth move this to a property.

        self.status = "PASS"

        # analysis graph
        self.graph = igraph.Graph(directed=True)

        # maintain a set of devices that have results.  A design could have
        # pseudo-devices, for example, that do not have results.

        self.devices = {
            dev_obj for dev_obj in design.devices.values() if not dev_obj.is_pseudo
        }

        # -----------------------------------------------------------------------------
        # Results-Map Data Structure
        # -----------------------------------------------------------------------------
        # key=device (object),
        # value=dict
        #   key=check-type,
        #   value=dict
        #       key=check-id,
        #       value=CheckResult
        # -----------------------------------------------------------------------------

        self.results_map: ResultMapT = defaultdict(lambda: defaultdict(dict))

        # maps any object to a graph-node.
        self.nodes_map: NodeObjIDMapT = bidict()

        # load all check results so they can be incorporated into the analysis graph.
        self._load_feature_results()

    def add_node(self, obj, **kwargs) -> igraph.Vertex:
        """
        Ensures that a node for the given object exists in the graph.  If it
        does exist the existing node is returned.  If it does not exist, a new
        node is created and returned.
        """
        if has_node := self.nodes_map.get(obj):
            return has_node

        self.nodes_map[obj] = node = self.graph.add_vertex(obj, **kwargs)
        return node

    def add_edge(self, source, target, **kwargs):
        self.graph.add_edge(
            self.nodes_map[source].index, self.nodes_map[target].index, **kwargs
        )

    def build(self):
        """
        This function is responsible for producing the services results graphs
        for each service in the design.
        """
        for svc in self.design.services.values():
            svc.build(ai=self)

    async def check(self):
        for svc in self.design.services.values():
            await svc.check(ai=self)
            self.analyze(svc)

    def show_report(self, console: Console):
        for svc in self.design.services.values():
            svc.build_report(ai=self)
            svc.show_report(console)

    # -------------------------------------------------------------------------
    #
    #                                Analyzer
    #
    # -------------------------------------------------------------------------

    def analyze(self, svc: "DesignService"):
        svc_node = self.nodes_map[svc]
        self._analyze_walk_design(svc, svc_node)
        self._analyze_walk_results(svc, svc_node)

    def _analyze_walk_design(self, svc: "DesignService", start_node: igraph.Vertex):
        edges = list(filter(lambda e: e["kind"] == "s", start_node.out_edges()))
        targets = [edge.target_vertex for edge in edges]
        for target in targets:
            self._analyze_walk_results(svc, target)

    def _analyze_walk_results(self, svc: "DesignService", start_node: igraph.Vertex):
        """
        Walk a design node set of result relationships.  If any of the results
        are FAIL, then set the design node status to "FAIL" and return.


        """
        walk = [start_node]

        while walk:
            node = walk.pop()
            edges = list(filter(lambda e: e["kind"] == "r", node.out_edges()))
            targets = [edge.target_vertex for edge in edges]

            for e_target in targets:
                # if the target node has a status of "FAIL", then we set the
                # overall service to "FAIL", set the starting node status to
                # FAIL, and add the failure check object to the list of failed
                # checks.

                if e_target["status"] == "FAIL":
                    self.nodes_map[svc]["status"] = "FAIL"
                    start_node["status"] = "FAIL"

                    # add the feature check to the failed list.
                    check = self.nodes_map.inv[e_target]
                    svc.failed.append(check)

                # if we've reached a design node, then stop this part of the walk.

                if e_target["kind"] == "d":
                    continue

                # otherwise add the target to the walk list to continue the
                # traversal.

                walk.append(e_target)

    # -------------------------------------------------------------------------
    #
    #                             PRIVATE METHODS
    #
    # -------------------------------------------------------------------------

    def _load_feature_results(self):
        for feat in self.design.features.values():
            for check_type in feat.check_collections:
                for device in self.devices:
                    result_objs = self._load_check_type_results(device, check_type)
                    self._add_result_nodes(device, feature=feat, results=result_objs)

    def _load_check_type_results(
        self, device: "Device", check_type: CheckCollectionT
    ) -> Iterator[dict]:
        # if the check results file does not exist, then return an empty
        # iterator so the calling scope is AOK.

        results_file = self._device_results_file(device, check_type)

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

    def _add_result_nodes(
        self, device: "Device", feature: "DesignFeature", results: Iterator[CheckResult]
    ):
        for res_obj in results:
            check = res_obj.check
            check_type = check.check_type

            # add the node to the design results-graph so features can
            # cross-functionally use them.
            self.nodes_map[res_obj] = self.graph.add_vertex(
                feature=feature.name,
                check_type=check_type,
                check_id=res_obj.check_id,
                status=res_obj.status,
                device=res_obj.device,
                kind="r",
            )

            self.results_map[device][check_type][res_obj.check_id] = res_obj

    @staticmethod
    def _device_results_file(device: "Device", check_type: CheckCollectionT) -> Path:
        check_name = check_type.get_name()
        base_dir = netcad_globals.g_netcad_checks_dir
        return (
            base_dir
            / device.design.name
            / device.name
            / "results"
            / f"{check_name}.json"
        )
