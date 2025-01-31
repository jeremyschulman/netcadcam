#  Copyright (c) 2025 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import ClassVar
from dataclasses import dataclass
from operator import itemgetter

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.table import Table

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.feats.vlans import InterfaceL2, VlanProfile
from netcad.feats.vlans.checks.check_switchports import SwitchportCheck

from .design_service import DesignService
from .graph_query import GraphQuery
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
    """
    The SwitchportService class is a DesignService that is responsible for
    managing the switchport feature checks originating from the topology
    provided.

    Graph Relationships
    -------------------
    # Design Relationships
        Interface.profile ->[d]-> Interface
        Device -[s]-> Interface

    # Service Relationships
        service ->[s]-> CheckSwitchports ->[r]-> swichport check result

    """

    @dataclass
    class Config:
        topology: TopologyService

    class CheckSwitchports(DesignServiceCheck):
        check_type: ClassVar[str] = "switchport"

    def __init__(self, *vargs, config: Config, **kwargs):
        super().__init__(*vargs, config=config, **kwargs)

        # key=if_name, value=if_obj
        self.interfaces: dict[str, DeviceInterface] = None
        self.vlans: set[VlanProfile] = set()

    def build_design_graph(self, ai: "ServicesAnalyzer"):
        """
        Add switchport nodes to the design that are related to their underlying
        interfaces.  Not all interfaces in the topology are running in Layer2
        switchport mode.  So we need to filter the list of interfaces.
        """

        self.interfaces = {
            if_obj.name: if_obj
            for if_obj in self.config.topology.interfaces
            if if_obj.profile and isinstance(if_obj.profile, InterfaceL2)
        }

        for if_obj in self.interfaces.values():
            self.vlans.update(if_obj.profile.vlans_used())
            # Interface Profile ->[s]-> Interface
            ai.add_service_edge(self, if_obj.profile, if_obj)

            # Device ->[s]-> Interface
            ai.add_service_edge(self, if_obj.device, if_obj)

    # -------------------------------------------------------------------------
    #
    #                             Reports
    #
    # -------------------------------------------------------------------------

    def build_results_graph(self, ai: "ServicesAnalyzer"):
        """
        Create a relationship between each of the switchport feature checks to
        the switchport design nodes.
        """

        service_check = SwitchportService.CheckSwitchports()
        ai.add_service_check(self, service_check)

        for if_obj in self.interfaces.values():
            # get the switchport check result object for the interface
            checkr_obj = ai.results_map[if_obj.device][SwitchportCheck.check_type_()][
                if_obj.name
            ]

            # Add a relation to the service level check to each of the underlying
            # device feature checks
            ai.add_check_edge(self, service_check, checkr_obj)

            # Switchport ->[r]-> CheckResult
            ai.add_check_edge(self, if_obj.profile, checkr_obj)

    def build_report(self, ai: "ServicesAnalyzer"):
        self.report = DesignServiceReport(
            title=f"Switchport Report: {self.name} - {len(self.interfaces)} total ports"
        )

        # ---------------------------------------------------------------------
        # Show the Vlans used
        # ---------------------------------------------------------------------

        table = Table("VLAN ID", "Name", "Description")
        for vlan in sorted(self.vlans, key=lambda i: i.vlan_id):
            table.add_row(str(vlan.vlan_id), vlan.name, vlan.description or "")

        self.report.add("VLANs", True, table)

        # ---------------------------------------------------------------------
        # starting with the service level check node, find all switchport
        # checks and group them by "PASS" / "FAIL"
        # ---------------------------------------------------------------------

        pass_fail = (
            GraphQuery(ai.graph)(
                *ai.graph.vs.select(
                    service=self.name,
                    check_type=self.CheckSwitchports.check_type,
                )
            )
            .out_()
            .groupby(itemgetter("status"))
        )

        pass_objs = map(ai.nodes_map.inv.__getitem__, pass_fail["PASS"])
        fail_objs = map(ai.nodes_map.inv.__getitem__, pass_fail["FAIL"])

        # ---------------------------------------------------------------------
        # Show the details of the passing ports
        # ---------------------------------------------------------------------

        table = Table("Device", "Interface", "Desc", "Results")

        for chk_obj in pass_objs:
            if_obj = self.interfaces[chk_obj.check_id]
            table.add_row(
                chk_obj.device,
                chk_obj.check_id,
                if_obj.desc,
                self.build_feature_logs_table(chk_obj),
            )

        self.report.add("Switchports", True, table)

        # ---------------------------------------------------------------------
        # if there are failed switchport nodes then create a table of these errors.
        # ---------------------------------------------------------------------

        if not pass_fail["FAIL"]:
            return

        table = Table("Device", "Interface", "Desc", "Results")
        for chk_obj in fail_objs:
            if_obj = self.interfaces[chk_obj.check_id]
            table.add_row(
                chk_obj.device,
                chk_obj.check_id,
                if_obj.desc,
                self.build_feature_logs_table(chk_obj),
            )

        self.report.add("Switchports", False, table)
