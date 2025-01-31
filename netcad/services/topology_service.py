#  Copyright (c) 2025 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Callable, ClassVar, Any
from collections import defaultdict
from dataclasses import dataclass
from itertools import chain

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from first import first
from rich.table import Table
from rich.pretty import Pretty
from rich.text import Text, Style
# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.checks import CheckStatus
from netcad.device import Device, DeviceInterface
from netcad.device.profiles import InterfaceL3

from netcad.feats.topology import TopologyDesignFeature
from netcad.feats.topology.checks.check_device_info import DeviceInformationCheck
from netcad.feats.topology.checks.check_interfaces import InterfaceCheck
from netcad.feats.topology.checks.check_cabling_nei import InterfaceCablingCheck
from netcad.feats.topology.checks.check_ipaddrs import IPInterfaceCheck
from netcad.feats.topology.checks.check_transceivers import TransceiverCheck

from .graph_query import GraphQuery
from .service_check import DesignServiceCheck
from .service_report import DesignServiceReport
from .design_service import DesignService
from .services_analyzer import ServicesAnalyzer

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class TopologyService(DesignService):
    """
    The purpose of the TopologyService class is to provide a service level view
    of the topology related to the set of interfaces that match the criteria
    defined in the config object passed to the constructor.

    The service design graph relates the
        (1) all device nodes to the Design node
        (2) all interface nodes to their respective Device node

    The service check graph relates:
        (1) all device feature checks to each Device node,
        (2) all interface feature checks to each Interface node.

    Attributes
    ----------
    config : TopologyServiceConfig
        The configuration object that defines the service criteria.

    devices : set[Device]
        The set of devices that are part of this specific topology

    interfaces : set[DeviceInterface]
        The set of device interfaces that are part of this specific topology

    """

    # -------------------------------------------------------------------------
    # Service Configuration
    # -------------------------------------------------------------------------

    @dataclass
    class Config:
        """This class is used to configure the topology service."""

        # reference to the topology design feature
        topology_feature: TopologyDesignFeature

        # function used to match interfaces that should be included in the service
        # generally, this will be a function that checks the interface profile
        # attributes, like "is_network".  The example callable in that case could
        # be a simple lambda function like:
        #
        #       lambda ifp: ifp.is_network

        match_interface_profile: Callable

    # -------------------------------------------------------------------------
    # Service Check Types
    # -------------------------------------------------------------------------

    class CheckCabling(DesignServiceCheck):
        """
        This check serves to validate the cabling between two interfaces.  While
        there are two separate checks on a feature basis, this service level check
        creates a relationship between the two so that we can reason about the
        overall status of the cabling.
        """

        check_type: ClassVar[str] = "topology.cabling"
        msrd: Any = None

        def details(self):
            return self.msrd

    def __init__(self, *vargs, config: Config, **kwargs):
        super().__init__(*vargs, **kwargs)
        self.config = config
        self.devices: set[Device] = None
        self.interfaces: set[DeviceInterface] = None

        self.match_interfaces()

        if not self.interfaces:
            raise ValueError(f"No interfaces found for service: {self.name}")

    def match_interfaces(self) -> bool:
        """
        Find all interfaces in the topology that match the service search
        criteria.
        """

        self.interfaces = {
            interface
            for device in self.design.devices.values()
            if not device.is_pseudo
            for interface in device.interfaces.values()
            if interface.profile
            and self.config.match_interface_profile(interface.profile)
        }

        self.devices = set(if_obj.device for if_obj in self.interfaces)

    # --------------------------------------------------------------------------
    #
    #                             Design
    #
    # --------------------------------------------------------------------------

    def build_design_graph(self, ai: ServicesAnalyzer):
        """
        This function is used to create the topology design graph relating
        devices to their respective interfaces.  The graph is directed from
        device to interfaces:
                (D) -> (I)
        """

        for dev_obj in self.devices:
            ai.add_design_node(dev_obj, kind_type="device", device=dev_obj.name)
            ai.add_service_edge(service=self, source=self, target=dev_obj)

        self._build_design_interfaces(ai)

    def _build_design_interfaces(self, ai: ServicesAnalyzer):
        for if_obj in self.interfaces:
            if ai.add_design_node(
                if_obj,
                kind_type="interface",
                device=if_obj.device.name,
                if_name=if_obj.name,
            ):
                # design edge between device and interface
                ai.add_design_edge(if_obj.device, if_obj)

            # always add service edge between device and interface
            ai.add_service_edge(self, if_obj.device, if_obj)

            # design edge betwee the interface profile and the interface
            if ai.add_design_node(
                if_obj.profile,
                kind_type="interface.profile",
                profile=if_obj.profile.name,
                device=if_obj.device.name,
                if_name=if_obj.name,
            ):
                # if.profile -> Interface
                ai.add_design_edge(if_obj.profile, if_obj)

            # always add service edge between interface profile and interface
            ai.add_service_edge(self, if_obj.profile, if_obj)

            # if there is an interface assigned to the profile, then add that
            # as a node in the graph.
            #
            # ipaddr -> if.profile

            if isinstance(if_obj.profile, InterfaceL3):
                if ai.add_design_node(if_obj.profile.if_ipaddr, kind_type="ipaddr"):
                    ai.add_design_edge(if_obj.profile.if_ipaddr, if_obj.profile)
                ai.add_service_edge(self, if_obj.profile.if_ipaddr, if_obj.profile)

    # --------------------------------------------------------------------------
    #
    #                             Results Graph
    #
    # --------------------------------------------------------------------------

    def build_results_graph(self, ai: ServicesAnalyzer):
        """
        This function is used to create the topology results graph relating the
        feature checks to the device and interface design nodes.
        """
        self._build_results_devices(ai)
        self._build_results_interfaces(ai)

    def _build_results_devices(self, ai: ServicesAnalyzer):
        """
        Associate the device-info check result to the device design node
        """

        for dev_obj in self.devices:
            check_obj = ai.results_map[dev_obj][DeviceInformationCheck.check_type_()][
                dev_obj.name
            ]
            ai.add_check_edge(self, dev_obj, check_obj)

    def _build_results_interfaces(self, ai: ServicesAnalyzer):
        """
        Associate each of the interface checks with the Interface design node.
        """
        if_check_types = [
            InterfaceCheck.check_type_(),
            IPInterfaceCheck.check_type_(),
            TransceiverCheck.check_type_(),
            InterfaceCablingCheck.check_type_(),
            # TODO: other checks, like lags?
        ]

        for if_obj in self.interfaces:
            for check_type in if_check_types:
                # if the interface does not have this specific check, for
                # example not all interfaces have transceivers, then we skip.

                if not (
                    if_check_obj := ai.results_map[if_obj.device][check_type].get(
                        if_obj.name
                    )
                ):
                    continue

                ai.add_check_edge(self, if_obj, if_check_obj)

    # -------------------------------------------------------------------------
    #
    #                             Checks
    #
    # -------------------------------------------------------------------------

    async def check(self, ai: ServicesAnalyzer):
        """Generate the service level checks"""
        self._check_cabling(ai)

    def _check_cabling(self, ai: ServicesAnalyzer):
        # create the top level cabling check node that will be the parent to
        # each of the individual interface cabling checks.

        top_node = self.CheckCabling()
        ai.add_service_check(self, top_node)

        # -----------------------------------------------------------------------------
        # first step is to filter the list of cabling to only those that could
        # be performing LLDP in this topology.  That means excluding virtual
        # interfaces, for example.
        # -----------------------------------------------------------------------------

        cabling = self.config.topology_feature.cabling

        def if_ok(if_obj: DeviceInterface) -> bool:
            return if_obj in self.interfaces and not if_obj.profile.is_virtual

        cables = [ends for ends in cabling.cables.values() if all(map(if_ok, ends))]

        # -----------------------------------------------------------------------------
        # create the 'topology interface peer check' results based on the
        # results of the individual interface cabling checks.
        # -----------------------------------------------------------------------------

        if_cable_check = InterfaceCablingCheck.check_type_()

        for if_a, if_b in cables:
            # TODO: not sure the checks are missing, the but measurement could
            #       be missing.  May need to account for that scenario.

            if_a_r = ai.results_map[if_a.device][if_cable_check][if_a.name]
            if_b_r = ai.results_map[if_b.device][if_cable_check][if_b.name]

            # check passes if for interface checks pass.

            ok = if_a_r.status == CheckStatus.PASS and if_b_r.status == CheckStatus.PASS
            ifp_r = self.CheckCabling(ok=ok)

            # -----------------------------------------------------------------
            # create the graph relationship between the service level check and
            # the device feature level checks.
            # -----------------------------------------------------------------

            ai.add_check_node(self, ifp_r)
            ai.add_check_edge(self, ifp_r, if_a_r)
            ai.add_check_edge(self, ifp_r, if_b_r)

            # add the cable-check node to the top-node for traveral later.
            ai.add_check_edge(self, top_node, ifp_r)

    # -------------------------------------------------------------------------
    #
    #                             Reports
    #
    # -------------------------------------------------------------------------

    def build_report(self, ai: ServicesAnalyzer):
        self.report = DesignServiceReport(title=f"Topology Service Report: {self.name}")
        self._build_report_devices(ai)
        self._build_report_interfaces(ai)
        self._build_report_cabling(ai)
        self._build_report_ipaddrs(ai)

    def _build_report_cabling(self, ai: ServicesAnalyzer):
        # ---------------------------------------------------------------------
        # get the top level topology cabling check node to determine the
        # overall status of the cabling checks.
        # ---------------------------------------------------------------------

        svc_cable_node = first(
            node
            for edge in ai.nodes_map[self].out_edges()
            if (node := edge.target_vertex)["check_type"]
            == self.CheckCabling.check_type
        )

        # ---------------------------------------------------------------------
        # Cabling report
        # ---------------------------------------------------------------------

        if pass_c := svc_cable_node["pass_count"]:
            self.report.add("Cabling", True, {"count": pass_c})

        if fail_c := svc_cable_node["fail_count"]:
            # TODO: add more details to the cabling failure report
            self.report.add("Cabling", False, {"count": fail_c})

    def _build_report_devices(self, ai: ServicesAnalyzer):
        """
        For device checks, we only care about the directly associated results,
        and not the associated interface results.  This means that a device may
        be in a "FAIL" status because of the associated interfaces errors.  But
        we do not want to report that condition; only the condition of
        specifically device results.
        """

        devices_ok = defaultdict(list)

        for dev_obj in self.devices:
            any_fail_results = (
                GraphQuery(ai.graph)(ai.nodes_map[dev_obj])
                .out_(kind="r", service=self.name)
                .node(status="FAIL")
                .nodes
            )

            devices_ok[not bool(any_fail_results)].append(dev_obj)

        self.report.add(
            "Devices", True, ", ".join(sorted([d.name for d in devices_ok[True]]))
        )

        if failed := devices_ok[False]:
            self.report.add(
                "Devices", False, ", ".join(sorted([d.name for d in failed]))
            )

    def build_report_interfaces_errors_table(self, ai: ServicesAnalyzer) -> Table:
        """
        This method is used to produce a Rich Table that contains the list of
        interface errors found on this topology.  This function is exposed so
        that other services can use it to build their own reports.
        """

        ifs_failed = [
            if_obj
            for if_obj in self.interfaces
            if ai.nodes_map[if_obj]["fail_count"] != 0
        ]

        # ------------------------------------------------------------------
        # Create a table for interface specific failure results
        # ------------------------------------------------------------------

        table = Table(
            "Device",
            "Interface",
            "Description",
            "Profile",
            "Status",
            show_lines=True,
            title=f"{len(ifs_failed)} Interfaces with issues",
            title_justify="left",
        )

        for if_obj in ifs_failed:
            if_checks = [
                ai.nodes_map.inv[edge.target_vertex]
                for edge in ai.nodes_map[if_obj].out_edges()
                if edge["kind"] == "r"
                if edge.target_vertex["status"] == "FAIL"
            ]

            for if_check in if_checks:
                ai.nodes_map[if_check]["reported"] = True

            fail_logs = [
                (if_check.check.check_type, log[1:])
                for if_check in if_checks
                for log in if_check.logs.root
                if log[0] == "FAIL"
            ]

            table.add_row(
                if_obj.device.name,
                if_obj.name,
                if_obj.desc,
                if_obj.profile.name,
                Pretty(fail_logs),
            )

        return table

    def _build_report_interfaces(self, ai: ServicesAnalyzer):
        """
        The "interfaces report" checks the interface design nodes for
        PASS/FAIL. If all are OK, then this report check passes.
        """

        if_good_objs = filter(
            lambda i: ai.nodes_map[i]["fail_count"] == 0, self.interfaces
        )

        if_table = Table("Device", "Interface", "Description", "Profile")

        for if_obj in sorted(if_good_objs, key=lambda i: i.device.name):
            if_table.add_row(
                if_obj.device.name, if_obj.name, if_obj.desc, if_obj.profile.name
            )

        self.report.add("Interfaces", True, if_table)

        table = self.build_report_interfaces_errors_table(ai=ai)
        if table.rows:
            self.report.add("Interfaces", False, table)

    def _build_report_ipaddrs(self, ai: ServicesAnalyzer):
        ipaddrs_ok = defaultdict(list)

        # collect the L3 interface check results
        for if_obj in self.interfaces:
            if isinstance(if_obj.profile, InterfaceL3):
                if_check = ai.results_map[if_obj.device][
                    IPInterfaceCheck.check_type_()
                ][if_obj.name]
                ipaddrs_ok[if_check.status].append(if_check)

        table = Table("Status", "Device", "Interface", "IP Address")
        for if_check in chain(
            ipaddrs_ok[CheckStatus.FAIL], ipaddrs_ok[CheckStatus.PASS]
        ):
            table.add_row(
                Text(
                    if_check.status,
                    Style(color="green" if if_check.status == "PASS" else "red"),
                ),
                if_check.device,
                if_check.check_id,
                if_check.check.expected_results.if_ipaddr,
            )

        self.report.add("IP Addresses", len(ipaddrs_ok[CheckStatus.FAIL]) == 0, table)
