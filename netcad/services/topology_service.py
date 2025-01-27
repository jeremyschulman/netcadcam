# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Callable, ClassVar, Any

from black.trans import defaultdict
# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

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
    check_type: ClassVar[str] = "topology.cabling"
    msrd: Any = None

    def details(self):
        return self.msrd


class TopologyService(DesignService):
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

        # -----------------------------------------------------------------------------
        # build the device -> interface design graph.  Initialize the status
        # value for each design node to "PASS".  This status will be updated
        # should the analyzer find that any related checks fail.
        # -----------------------------------------------------------------------------

        for dev_obj in self.devices:
            ai.add_design_node(dev_obj, kind_type="device")
            ai.add_edge(self, dev_obj, kind="s", service=self.name)

        for if_obj in self.interfaces:
            ai.add_design_node(
                if_obj,
                kind_type="interface",
                device=if_obj.device.name,
                if_name=if_obj.name,
            )

            # design edge between device and interface
            ai.add_edge(if_obj.device, if_obj, kind="d")

            # service edge between device and interface
            ai.add_edge(if_obj.device, if_obj, kind="s", service=self.name)

    # --------------------------------------------------------------------------
    #
    #                             Results
    #
    # --------------------------------------------------------------------------

    def build_results_graph(self, ai: ServicesAnalyzer):
        self._build_results_deviceinfo(ai)
        self._build_results_interfaces(ai)

    def _build_results_deviceinfo(self, ai: ServicesAnalyzer):
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
                if not (
                    if_check_obj := ai.results_map[if_obj.device][check_type].get(
                        if_obj.name
                    )
                ):
                    continue

                ai.add_edge(if_obj, if_check_obj, kind="r", service=self.name)

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
            ai.add_edge(ifp_r, if_a_r, kind="r", service=self.name)
            ai.add_edge(ifp_r, if_b_r, kind="r", service=self.name)

            # add the cable-check node to the top-node for traveral later.
            ai.add_edge(top_node, ifp_r, kind="r", service=self.name)

    # -------------------------------------------------------------------------
    #
    #                             Reports
    #
    # -------------------------------------------------------------------------

    def build_report(self, ai: ServicesAnalyzer):
        svc_node = ai.nodes_map[self]

        check_nodes = {
            t["name"].__class__: ai.nodes_map.inv[t]
            for t in [e.target_vertex for e in svc_node.out_edges() if e["kind"] == "s"]
        }

        self.report = DesignServiceReport(title=f"Topology Service Report: {self.name}")

        self._build_report_devices(ai, self.report)
        self._build_report_interfaces(ai, self.report)

        # ---------------------------------------------------------------------
        # Cabling report
        # ---------------------------------------------------------------------

        svc_cable_node = ai.nodes_map[check_nodes[TopologyCheckCabling]]

        if pass_c := svc_cable_node["pass_count"]:
            self.report.add("Cabling", True, {"count": pass_c})

        if fail_c := svc_cable_node["fail_count"]:
            self.report.add("Cabling", False, {"count": fail_c})

        if self.failed:
            self.failed = [err for err in self.failed if not err["reported"]]

        if self.failed:
            self.report.add(
                "Unreported Feature Issues",
                False,
                details=self.build_features_report_table(),
            )

    def _build_report_devices(self, ai: ServicesAnalyzer, report: DesignServiceReport):
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

        report.add("Devices", True, {"count": len(devices_ok[True])})

        if not (devs_failed := devices_ok[False]):
            return

        # TODO: need to add more detailed failure reporting.  For now just
        #       going to show the count of failed devices.

        report.add("Devices", False, {"count": len(devs_failed)})

    def _build_report_interfaces(
        self, ai: ServicesAnalyzer, report: DesignServiceReport
    ):
        # ---------------------------------------------------------------------
        # The "interfaces report" checks the interface design nodes for
        # PASS/FAIL. If all are OK, then this report check passes.
        # ---------------------------------------------------------------------

        interfaces_ok = defaultdict(list)
        for if_obj in self.interfaces:
            node = ai.nodes_map[if_obj]
            interfaces_ok[node["status"] == "PASS"].append(if_obj)

        report.add("Interfaces", True, {"count": len(interfaces_ok[True])})

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

        report.add("Interfaces", False, table)
