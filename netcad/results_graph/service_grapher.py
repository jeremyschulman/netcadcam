#  Copyright (c) 2022 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import (
    Iterator,
    TYPE_CHECKING,
    Optional,
    Set,
    List,
    ValuesView,
    Sequence,
    Type,
)
from itertools import chain

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
from netcad.checks import CheckCollectionT, CheckResult, Check, CheckStatus

if TYPE_CHECKING:
    from netcad.design import DesignService

from .results_graph import ResultsGraph


class ServiceResultsGrapher:
    def __init__(self, drg: ResultsGraph, service: "DesignService"):
        self.design = drg.design
        self.service = service
        self.graph = drg.graph
        self.results_map = drg.results_map
        self.nodes_map = drg.nodes_map

        # The devices participating in the graph for this service.  These are
        # only those that have results data.  So HostDevice devices, for
        # example, will not be included in the results graph, even though they
        # are included in the service.
        self.devices: List[Device] | None = None

        # The set of results that were added to the graph for this specific
        # service.  These present the results loaded from the `devices`.
        self.nodes: Set[CheckResult] = set()

    # ---------------------------------------------------------------------
    #
    #  Grapher _interfacing_ methods used during the "build" process.
    #
    # ---------------------------------------------------------------------

    def build_graph_nodes(self):
        """
        This function is used to ingest the check results file payloads (JSON)
        from the persisted files, create the graph node objects and store them
        into the `nodes_map` and `results_map` collections.
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
                self._add_result_nodes(device, result_objs)

    def build_graph_edges(self):
        """Required by subclass"""
        pass

    # ---------------------------------------------------------------------
    # Utility Methods
    # ---------------------------------------------------------------------

    def add_graph_edges_hubspkes(
        self, hub_check_type: Type[Check], spoke_check_types: Sequence[Type[Check]]
    ):
        ct_hub = hub_check_type.check_type_()
        ct_spokes = [check_type.check_type_() for check_type in spoke_check_types]

        for dev in self.devices:
            res_map = self.results_map[dev]

            hub_r = res_map[ct_hub][dev.name]

            # associate the port, single-slave, and exclusive checks to the
            # ptp-system node

            spokes_r = chain.from_iterable(
                res_map[check_type].values() for check_type in ct_spokes
            )

            for spoke_r in spokes_r:
                self.add_graph_edge(source=hub_r, target=spoke_r)

    def get_device_results(
        self, device: Device, check_type: Type[Check]
    ) -> ValuesView[CheckResult]:
        res_map = self.results_map[device]
        return res_map[check_type.check_type_()].values()

    def get_device_result(
        self, device: Device, check_type: Type[Check], check_id: str
    ) -> CheckResult | None:
        res_map = self.results_map[device]
        return res_map[check_type.check_type_()].get(check_id)

    @staticmethod
    def default_edge_kind(source, target):
        f_ct = source.check.check_type
        t_ct = target.check.check_type
        return f"checked,{f_ct},{t_ct}"

    def add_graph_edge(
        self,
        source: CheckResult,
        target: CheckResult,
        kind: Optional[str] = None,
        **attrs,
    ):
        """
        Create a graph edge between the source and target nodes.

        Parameters
        ----------
        source:
            The source check-result instance

        target:
            The target check-result instance

        kind: str, optional
            The edge kind attribute,

        Other Parameters
        ----------------
        Any other kwargs given are added as edge attributes in the graph.

        The follow edge attributes are automatically defined:
            kind: the "kind" of the edge, as given or default-value
            status: the status of the source result-check (pass/fail)

        """
        source_id = self.nodes_map[source]
        target_id = self.nodes_map[target]

        # set the status to pass iff both sides pass
        status = (
            CheckStatus.PASS
            if source.status == target.status == CheckStatus.PASS
            else CheckStatus.FAIL
        )
        attrs.setdefault("kind", kind or self.default_edge_kind(source, target))
        attrs.setdefault("status", status)

        self.graph.add_edge(source=source_id, target=target_id, **attrs)

    # ---------------------------------------------------------------------
    #
    # Ingesting the CheckResults payloads from JSON files.
    #
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

    def _add_result_nodes(self, device: Device, results: Iterator[CheckResult]):
        for res_obj in results:
            check = res_obj.check
            check_type = check.check_type

            # add the node in the graph instance
            node: igraph.Vertex = self.graph.add_vertex(
                check_id=res_obj.check_id,
                check_type=check_type,
                status=res_obj.status,
                device=res_obj.device,
                service=self.service.name,
            )

            # add the node to _this_service_ grapher
            self.nodes.add(res_obj)

            # add the node to the design results-graph so services can
            # cross-functionally use them.
            self.nodes_map[res_obj] = node.index
            self.results_map[device][check_type][res_obj.check_id] = res_obj
