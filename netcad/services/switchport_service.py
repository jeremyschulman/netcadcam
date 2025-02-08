#  Copyright (c) 2025 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import ClassVar
from dataclasses import dataclass
from operator import itemgetter
from itertools import chain

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.table import Table

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device.profiles import InterfaceProfile
from netcad.feats.vlans import InterfaceL2, VlanProfile, InterfaceVlan
from netcad.feats.vlans.checks.check_switchports import SwitchportCheck
from netcad.feats.topology.checks.check_ipaddrs import IPInterfaceCheck

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
        self.config: SwitchportService.Config = config
        super().__init__(*vargs, config=config, **kwargs)

        # key=if_name, value=if_obj
        self.interfaces: dict[str, DeviceInterface] = None

        # set of all VLANs used by the switchports
        self.vlans: set[VlanProfile] = set()

        # the topology service that is used to find the SVI interfaces
        self.svi_topology: TopologyService = None

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
            # keep track of all VLANs used by the switchports
            self.vlans.update(if_obj.profile.vlans_used())

            # Interface Profile ->[s]-> Interface
            ai.add_service_edge(self, if_obj.profile, if_obj)

            # Device ->[s]-> Interface
            ai.add_service_edge(self, if_obj.device, if_obj)

        # ---------------------------------------------------------------------
        # now that we have the VLANs, we can go back and find all the VLAN SVI
        # interfaces.  We will create an "internal" topology service of just
        # the SVIs so that we can validate the IP address configuration.
        # ---------------------------------------------------------------------

        def is_my_svi(_ipf: InterfaceProfile):
            return isinstance(_ipf, InterfaceVlan) and _ipf.vlan in self.vlans

        self.svi_topology = TopologyService(
            design=self.design,
            name=f"{self.name}.topology.svi",
            owner=self.owner,
            is_subservice=True,
            config=TopologyService.Config(
                topology_feature=self.config.topology.config.topology_feature,
                match_interface_profile=is_my_svi,
            ),
        )

        ai.services_queue.appendleft(self.svi_topology)

    # -------------------------------------------------------------------------
    #
    #                             Results Graph
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

    # -------------------------------------------------------------------------
    #
    #                             Reports Table
    #
    # -------------------------------------------------------------------------

    def build_report(self, ai: "ServicesAnalyzer", flags: dict):
        self.report = DesignServiceReport(
            title=f"Switchport Report: {self.name} - {len(self.interfaces)} total ports"
        )

        self._build_report_vlans(flags)
        self._build_report_switchports(ai, flags)
        self._build_report_svi(ai, flags)

    def _build_report_vlans(self, flags):
        # ---------------------------------------------------------------------
        # if we do not want to see the details on the VLANs, then show a count
        # of the VLANs.
        # ---------------------------------------------------------------------

        if not flags.get("all_results"):
            self.report.add("VLANs", True, {"count": len(self.vlans)})
            return

        # ---------------------------------------------------------------------
        # Oterwise, show the details on Vlans used
        # ---------------------------------------------------------------------

        table = Table("VLAN ID", "Name", "Description")
        for vlan in sorted(self.vlans, key=lambda i: i.vlan_id):
            table.add_row(str(vlan.vlan_id), vlan.name, vlan.description or "")

        self.report.add("VLANs", True, table)

    def _build_report_switchports(self, ai: "ServicesAnalyzer", flags: dict):
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

        if not flags.get("all_results"):
            self.report.add("Switchports", True, {"count": len(set(pass_objs))})
        else:
            table = Table("Device", "Interface", "Desc", "Logs")

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

        table = Table("Device", "Interface", "Desc", "Logs")
        for chk_obj in fail_objs:
            if_obj = self.interfaces[chk_obj.check_id]
            table.add_row(
                chk_obj.device,
                chk_obj.check_id,
                if_obj.desc,
                self.build_feature_logs_table(chk_obj),
            )

        self.report.add("Switchports", False, table)

    def _build_report_svi(self, ai: ServicesAnalyzer, flags: dict):
        # find all the IP address check nodes for this service and group them
        # by "PASS" / "FAIL"

        ipaddr_check_nodes = (
            GraphQuery(ai.graph)(ai.nodes_map[self.config.topology])
            .out_()
            .node(kind_type="interface")
            .out_(kind="r")
            .node(check_type=IPInterfaceCheck.check_type_())
            .groupby(itemgetter("status"))
        )

        # if everything passes, but we do not want to see the details, then
        # simply show the pass count.

        if not ipaddr_check_nodes["FAIL"] and not flags.get("all_results"):
            self.report.add("SVIs", True, {"count": len(ipaddr_check_nodes["PASS"])})
            return

        # if we are here, then it means we either have failures or we want to
        # see the details of all SVIs checks.  We are going to have two
        # separaete line items in the report table, one for PASS and another.
        # for fail.

        for status, chk_nodes in chain(ipaddr_check_nodes.items()):
            table = Table("Device", "Interface", "IP Address", "Logs")
            chk_objs = map(ai.nodes_map.inv.__getitem__, chk_nodes)

            # sort the checks by device name
            for chk_obj in sorted(chk_objs, key=lambda c: c.device):
                # only show details for failed checks.

                deets = (
                    self.build_feature_logs_table(chk_obj) if status == "FAIL" else None
                )

                table.add_row(
                    chk_obj.device,
                    chk_obj.check_id,
                    chk_obj.measurement.if_ipaddr,
                    deets,
                )

            if table.rows:
                self.report.add("SVIs", status == "PASS", table)
