#  Copyright (c) 2025 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import ClassVar
from dataclasses import dataclass

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.table import Table

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.feats.vlans import InterfaceL2
from netcad.feats.vlans.checks.check_switchports import SwitchportCheck

from .design_service import DesignService
from .service_report import DesignServiceReport
from .service_check import DesignServiceCheck
from .topology_service import TopologyService
from .services_analyzer import ServicesAnalyzer
from ..device import DeviceInterface


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class SwitchportService(DesignService):
    @dataclass
    class Config:
        topology: TopologyService

    class CheckSwitchports(DesignServiceCheck):
        check_type: ClassVar[str] = "switchport"

    def __init__(self, *vargs, config: Config, **kwargs):
        super().__init__(*vargs, config=config, **kwargs)
        self.interfaces: list[DeviceInterface] = None

    def build_design_graph(self, ai: "ServicesAnalyzer"):
        """
        Add switchport nodes to the design that are related to their underlying
        interfaces.  Not all interfaces in the topology are running in Layer2
        switchport mode.  So we need to filter the list of interfaces.
        """

        self.interfaces = [
            if_obj
            for if_obj in self.config.topology.interfaces
            if if_obj.profile and isinstance(if_obj.profile, InterfaceL2)
        ]

        for if_obj in self.interfaces:
            # using the interface profile as "switchport" anchoring instance
            # object for the graph vertext relationship.

            ai.add_design_node(
                if_obj.profile,
                kind_type="interface.l2",
                device=if_obj.device,
                interface=if_obj.name,
            )

            # Switchport ->[d]-> Interface
            ai.add_design_edge(if_obj.profile, if_obj)

            # Create a design service edge between the Device and Interface
            # Device ->[s]-> Interface
            ai.add_service_edge(self, if_obj.device, if_obj)

    def build_results_graph(self, ai: "ServicesAnalyzer"):
        """
        Create a relationship between each of the switchport feature checks to
        the switchport design nodes.
        """

        service_check = SwitchportService.CheckSwitchports()
        ai.add_service_check(self, service_check)

        for if_obj in self.interfaces:
            # get the switchport check result object for the interface
            checkr_obj = ai.results_map[if_obj.device][SwitchportCheck.check_type_()][
                if_obj.name
            ]

            # Add a relation to the service level check to each of the underlying
            # device feature checks
            ai.add_results_edge(self, service_check, checkr_obj)

            # Switchport ->[r]-> CheckResult
            ai.add_results_edge(self, if_obj.profile, checkr_obj)

    def build_report(self, ai: "ServicesAnalyzer"):
        self.report = DesignServiceReport(
            title=f"Switchport Report: {self.name} - {len(self.interfaces)} total ports"
        )
        svc_node = ai.nodes_map[self]

        self.report.add("Switchports", True, {"count": svc_node["pass_count"]})

        # starting with the service level check node, find all switchport
        # checks that are in the failed state.

        svc_check = ai.graph.vs.select(
            service=self.name,
            kind="r",
            check_type=SwitchportService.CheckSwitchports.check_type,
        )[0]

        failed = filter(
            lambda x: x["status"] == "FAIL", svc_check.neighbors(mode="out")
        )

        # if there are failed switchport nodes then create a table of these errors.

        if not svc_node["fail_count"]:
            return

        table = Table("Device", "Interface", "Report")
        for node in failed:
            obj = ai.nodes_map.inv[node]
            table.add_row(obj.device, obj.check_id, self.build_feature_logs_table(obj))

        self.report.add("Switchports", False, table)
