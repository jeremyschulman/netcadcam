#  Copyright (c) 2025 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import TYPE_CHECKING, Iterator
from collections import defaultdict, deque

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from bidict import bidict
import igraph
from rich.console import Console
from sqlalchemy.dialects.postgresql import insert

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

if TYPE_CHECKING:
    from netcad.device import Device
    from netcad.design import Design, DesignFeature

from netcam.db import db_connect
from netcam.db.db_check_results import db_check_results_get

from ..checks import CheckCollectionT, CheckResult, CheckStatus
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
        # key=device (Device),
        # value=dict
        #   key=check-type (str),
        #   value=dict
        #       key=check-id (str),
        #       value=CheckResult
        # -----------------------------------------------------------------------------

        self.results_map: ResultMapT = defaultdict(lambda: defaultdict(dict))

        # maps any object to a graph-node.
        self.nodes_map: NodeObjIDMapT = bidict()

        # this queue is used for processing services; so that a service can
        # define a subservice within itself, and the subservice can be
        # processed after the parent service is processed.
        self.services_queue = deque()

        self.db = db_connect(db_name=self.design.name)
        self.db_obj_map = bidict()

        # load all check results so they can be incorporated into the analysis graph.
        self._load_feature_results()

    # -------------------------------------------------------------------------
    # node methods
    # -------------------------------------------------------------------------

    def add_node(self, obj, **kwargs) -> bool:
        """
        Ensures that a node for the given object exists in the graph.  This
        function returns True when the node is created and False when the
        existing node is found.

        When created the node is added to the nodes_map dictionary.

        Returns
        -------
        True when the node was created
        False when the node already existed
        """
        if self.nodes_map.get(obj):
            return False

        self.nodes_map[obj] = self.graph.add_vertex(obj, **kwargs)
        return True

    def add_service_node(self, service: "DesignService"):
        self.add_node(
            service,
            kind="s",
            kind_type=service.__class__.__name__,
            service=service.name,
            pass_count=0,
            fail_count=0,
            status="PASS",
        )

    def add_design_node(self, obj, kind_type, **kwargs):
        return self.add_node(
            obj,
            kind="d",
            pass_count=0,
            fail_count=0,
            kind_type=kind_type,
            status="PASS",
            **kwargs,
        )

    def add_check_node(self, svc, obj, **kwargs):
        self.add_node(
            obj,
            kind="r",
            pass_count=0,
            fail_count=0,
            check_type=obj.check_type,
            service=svc.name,
            status="PASS",
            **kwargs,
        )

    def add_service_check(self, svc, obj, **kwargs):
        self.add_check_node(svc, obj, **kwargs)
        self.add_edge(svc, obj, kind="s", service=svc.name)

    # -------------------------------------------------------------------------
    # edge methods
    # -------------------------------------------------------------------------

    def add_edge(self, source, target, **kwargs):
        self.graph.add_edge(
            self.nodes_map[source].index, self.nodes_map[target].index, **kwargs
        )

    def add_design_edge(self, source, target, **kwargs):
        self.add_edge(source, target, kind="d", **kwargs)

    def add_service_edge(self, service, source, target, **kwargs):
        self.add_edge(source, target, kind="s", service=service.name, **kwargs)

    def add_check_edge(self, service, source, target, **kwargs):
        kwargs.setdefault("stop", False)
        self.add_edge(source, target, kind="r", service=service.name, **kwargs)

    # -------------------------------------------------------------------------
    #
    #                          Primary Analyzer Actions
    #
    # -------------------------------------------------------------------------

    def build(self):
        """
        This function is responsible for producing the services results graphs
        for each service in the design.
        """
        self.services_queue.extend(self.design.services.values())
        while True:
            try:
                svc = self.services_queue.popleft()
            except IndexError:
                break
            svc.build(ai=self)

    async def check(self):
        for svc in self.design.services.values():
            await svc.check(ai=self)
            self.analyze(svc)

    def build_reports(self, flags):
        for svc in self.design.services.values():
            svc.build_report(ai=self, flags=flags)

    def show_reports(self, console: Console):
        for svc in self.design.services.values():
            if svc.is_subservice:
                continue

            console.print("\n\n", svc.report.table)

    # -------------------------------------------------------------------------
    #
    #                                Analyzer
    #
    # -------------------------------------------------------------------------

    def analyze(self, svc: "DesignService"):
        node = self.nodes_map[svc]

        self._analyze_service_node(svc, node)

        if node["fail_count"]:
            node["status"] = "FAIL"
            svc.status = "FAIL"

    def _analyze_service_node(self, svc: "DesignService", start_node: igraph.Vertex):
        edges = [
            edge
            for edge in start_node.out_edges()
            if edge["service"] == svc.name and not edge["stop"]
        ]

        targets = [edge.target_vertex for edge in edges]

        for target in targets:
            if target["check_id"] and target["status"] == "FAIL":
                svc.failed.append(target)

            self._analyze_service_node(svc, target)

            try:
                start_node["pass_count"] += target["pass_count"]
                start_node["fail_count"] += target["fail_count"]

            except TypeError:
                raise ValueError(
                    f"Analyzer failed due to missing counters in node: {target.attributes()}"
                )

    def service_graph(self, svc: "DesignService") -> Iterator[DesignService]:
        """
        This function returns the set of service nodes that are associated with the given service.
        """
        walk_nodes = [self.nodes_map[svc]]
        svc_nodes = list()

        while walk_nodes:
            if (node := walk_nodes.pop()) in svc_nodes:
                continue

            svc_name = node["service"]
            svc_nodes.append(node)

            edges = (
                edge
                for edge in node.all_edges()
                if edge["kind"] == "s" and edge["service"] == svc_name
            )

            next_nodes = (
                vertex
                for edge in edges
                for vertex in edge.vertex_tuple
                if vertex["kind"] == "s" and vertex not in svc_nodes
            )

            walk_nodes.extend(next_nodes)

        return map(self.nodes_map.inverse.get, svc_nodes)

    # -------------------------------------------------------------------------
    #
    #                             Database Methods
    #
    # -------------------------------------------------------------------------

    def db_upsert(self, table, key, **kwargs):
        stmt = insert(table).values(**kwargs)

        stmt = stmt.on_conflict_do_update(
            index_elements=key,
            set_={"node_id": stmt.excluded.node_id},
            where=(table.node_id != stmt.excluded.node_id),
        )

        self.db.execute(stmt)
        self.db.commit()

        filter_by = {k: kwargs[k] for k in key}
        return self.db.query(table).filter_by(**filter_by).first()

    def db_add(self, table, **kwargs):
        self.db.add(table(**kwargs))
        self.db.commit()

    def db_find(self, table, **filter_by):
        return self.db.query(table).filter_by(**filter_by).first()

    # -------------------------------------------------------------------------
    #
    #                             PRIVATE METHODS
    #
    # -------------------------------------------------------------------------

    def _load_feature_results(self):
        for feat in self.design.features.values():
            for collection in feat.check_collections:
                for device in self.devices:
                    result_objs = self._load_check_type_results(
                        feat, device, collection
                    )
                    self._add_result_nodes(device, feature=feat, results=result_objs)

    def _load_check_type_results(
        self,
        feature: "DesignFeature",
        device: "Device",
        collection: CheckCollectionT,
    ) -> Iterator[dict]:
        # if the check results file does not exist, then return an empty
        # iterator so the calling scope is AOK.

        results = db_check_results_get(
            self.db, device.name, feature.name, collection=collection.name
        )

        # TODO: for now only include the PASS/FAIL status results.  We should
        #       add the INFO nodes to the graph as there could be meaningful
        #       use of these nodes for report processing.

        return (
            collection.parse_result(res_obj)
            for res_obj in results
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
            if res_obj.status == CheckStatus.PASS:
                counts = {"pass_count": 1, "fail_count": 0}
            else:
                counts = {"pass_count": 0, "fail_count": 1}

            self.nodes_map[res_obj] = self.graph.add_vertex(
                feature=feature.name,
                check_type=check_type,
                check_id=res_obj.check_id,
                status=str(res_obj.status),
                device=res_obj.device,
                kind="r",
                **counts,
            )

            self.results_map[device][check_type][res_obj.check_id] = res_obj
