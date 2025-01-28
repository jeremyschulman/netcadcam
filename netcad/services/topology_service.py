#  Copyright (c) 2025 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Callable, ClassVar, Any
from collections import defaultdict

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from first import first
from pydantic import BaseModel, ConfigDict
from rich.table import Table
from rich.pretty import Pretty

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.checks import CheckStatus
from netcad.device import Device, DeviceInterface

from netcad.feats.topology import TopologyDesignFeature
from netcad.feats.topology.checks.check_device_info import DeviceInformationCheck
from netcad.feats.topology.checks.check_interfaces import InterfaceCheck
from netcad.feats.topology.checks.check_cabling_nei import InterfaceCablingCheck
from netcad.feats.topology.checks.check_ipaddrs import IPInterfaceCheck
from netcad.feats.topology.checks.check_transceivers import TransceiverCheck

from .service_check import DesignServiceCheck
from .service_report import DesignServiceReport
from .design_service import DesignService
from .services_analyzer import ServicesAnalyzer

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class TopologyServiceConfig(BaseModel):
    """This class is used to configure the topology service."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # reference to the topology design feature
    topology_feature: TopologyDesignFeature

    # function used to match interfaces that should be included in the service
    # generally, this will be a function that checks the interface profile
    # attributes, like "is_network".  The example callable in that case could
    # be a simple lambda function like:
    #
    #       lambda ifp: ifp.is_network

    match_interface_profile: Callable


class TopologyCheckCabling(DesignServiceCheck):
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

    def __init__(self, *vargs, config: TopologyServiceConfig, **kwargs):
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
            ai.add_design_node(dev_obj, kind_type="device")
            ai.add_service_edge(self, self, dev_obj)

        for if_obj in self.interfaces:
            ai.add_design_node(
                if_obj,
                kind_type="interface",
                device=if_obj.device.name,
                if_name=if_obj.name,
            )

            # design edge between device and interface
            ai.add_design_edge(if_obj.device, if_obj)

            # service edge between device and interface
            ai.add_service_edge(self, if_obj.device, if_obj)

    # --------------------------------------------------------------------------
    #
    #                             Results
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
            ai.add_edge(dev_obj, check_obj, kind="r", service=self.name)

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

        top_node = TopologyCheckCabling()
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
            ifp_r = TopologyCheckCabling(ok=ok)

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

    def _build_report_cabling(self, ai: ServicesAnalyzer):
        # ---------------------------------------------------------------------
        # get the top level topology cabling check node to determine the
        # overall status of the cabling checks.
        # ---------------------------------------------------------------------

        svc_cable_node = first(
            node
            for edge in ai.nodes_map[self].out_edges()
            if (node := edge.target_vertex)["check_type"]
            == TopologyCheckCabling.check_type
        )

        # ---------------------------------------------------------------------
        # Cabling report
        # ---------------------------------------------------------------------

        if pass_c := svc_cable_node["pass_count"]:
            self.report.add("Cabling", True, {"count": pass_c})

        if fail_c := svc_cable_node["fail_count"]:
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
            dev_checks_fail = [
                ai.nodes_map.inv[node]
                for edge in ai.nodes_map[dev_obj].out_edges()
                if edge["kind"] == "r" and edge["service"] == self.name
                if (node := edge.target_vertex)["status"] == "FAIL"
            ]
            devices_ok[not dev_checks_fail].append(dev_obj)

        self.report.add("Devices", True, {"count": len(devices_ok[True])})

        if not (devs_failed := devices_ok[False]):
            return

        # TODO: need to add more detailed failure reporting.  For now just
        #       going to show the count of failed devices.

        self.report.add("Devices", False, {"count": len(devs_failed)})

    def _build_report_interfaces(self, ai: ServicesAnalyzer):
        # ---------------------------------------------------------------------
        # The "interfaces report" checks the interface design nodes for
        # PASS/FAIL. If all are OK, then this report check passes.
        # ---------------------------------------------------------------------

        interfaces_ok = defaultdict(list)
        for if_obj in self.interfaces:
            node = ai.nodes_map[if_obj]
            interfaces_ok[node["status"] == "PASS"].append(if_obj)

        self.report.add("Interfaces", True, {"count": len(interfaces_ok[True])})

        if not (ifs_failed := interfaces_ok[False]):
            return

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

        self.report.add("Interfaces", False, table)
