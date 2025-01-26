# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Callable, Literal
from dataclasses import dataclass
# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, ConfigDict
from rich.console import Console
from rich.table import Table
from rich.text import Text, Style

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


class TopologyCheckCabling(BaseModel):
    service: str
    feature: str
    kind: str = "r"
    kind_type: str = "topology.cabling"
    status: Literal["PASS", "FAIL"]

    def __hash__(self):
        return id(self)


@dataclass
class TopologyServiceReport:
    device_failures: list[Device]
    interface_failures: list[DeviceInterface]
    cabling_failures: list[TopologyCheckCabling]


class TopologyService(DesignService):
    CHECKS = [TopologyCheckCabling]

    def __init__(self, *vargs, config: TopologyServiceConfig, **kwargs):
        super().__init__(*vargs, **kwargs)
        self.config = config
        self.devices: set[Device] = None
        self.interfaces: set[DeviceInterface] = None
        self.report = None

        if not self.match_interfaces():
            raise ValueError(f"No interfaces found for service: {self.name}")

    def match_interfaces(self) -> bool:
        # find all interfaces from non-pseudo devices that match the profile
        # criteria

        self.interfaces = {
            interface
            for device in self.design.devices.values()
            if not device.is_pseudo
            for interface in device.interfaces.values()
            if interface.profile
            and self.config.match_interface_profile(interface.profile)
        }

        if not self.interfaces:
            return False

        self.devices = set(if_obj.device for if_obj in self.interfaces)
        return True

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
            ai.add_node(
                dev_obj,
                kind_type="device",
                device=dev_obj.name,
                kind="d",
                status="PASS",
            )

            # service edge between service and device
            ai.add_edge(self, dev_obj, kind="s", serivce=self.name)

        for if_obj in self.interfaces:
            ai.add_node(
                if_obj,
                kind="d",
                kind_type="interface",
                device=if_obj.device.name,
                if_name=if_obj.name,
                status="PASS",
            )

            # design edge between device and interface
            ai.add_edge(if_obj.device, if_obj, kind="d")

            # service edge between device and interface
            ai.add_edge(if_obj.device, if_obj, kind="s", service=self.name)

            # service edge between service and interface
            ai.add_edge(self, if_obj, kind="s", service=self.name)

    def build_results_graph(self, ai: ServicesAnalyzer):
        devinfo_checks_map = {
            dev_obj: ai.results_map[dev_obj][DeviceInformationCheck.check_type_()][
                dev_obj.name
            ]
            for dev_obj in self.devices
        }

        # -----------------------------------------------------------------------------
        # associate the device-info check result to the device design object.
        # -----------------------------------------------------------------------------

        for dev_obj, check_r_obj in devinfo_checks_map.items():
            ai.add_edge(dev_obj, check_r_obj, kind="r", service=self.name)
            ai.add_edge(check_r_obj, dev_obj, kind="d", service=self.name)

        # -----------------------------------------------------------------------------
        # add all interface checks to the interface node.
        # -----------------------------------------------------------------------------

        if_check_types = [
            InterfaceCheck.check_type_(),
            IPInterfaceCheck.check_type_(),
            TransceiverCheck.check_type_(),
            InterfaceCablingCheck.check_type_(),
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
                ai.add_edge(if_check_obj, if_obj, kind="d", service=self.name)

    async def check(self, ai: ServicesAnalyzer):
        """
        This function is used to generate service-level checkss.  The only
        check for the topology service is to check whether the cabline between
        interfaces are correct.
        """

        # use the cabling from the topology feature to create the "topology
        # interface peer check".

        feat = self.config.topology_feature

        # -----------------------------------------------------------------------------
        # first step is to filter the list of cabling to only those with
        # interfaces matching the topology service interfaces set and are not
        # virtual interfaces, like port-channels.
        # -----------------------------------------------------------------------------

        def if_ok(if_obj: DeviceInterface) -> bool:
            return if_obj in self.interfaces and not if_obj.profile.is_virtual

        cables = [
            ends for ends in feat.cabling.cables.values() if all(map(if_ok, ends))
        ]

        # -----------------------------------------------------------------------------
        # create the 'topology interface peer check' results based on the
        # results of the individual interface cabling checks.
        # -----------------------------------------------------------------------------

        if_cable_check = InterfaceCablingCheck.check_type_()

        for if_a, if_b in cables:
            if_a_r = ai.results_map[if_a.device][if_cable_check].get(if_a.name)
            if_b_r = ai.results_map[if_b.device][if_cable_check].get(if_b.name)

            if not (if_a_r and if_b_r):
                ifp_r = TopologyCheckCabling(
                    status="FAIL", service=self.name, feature=feat.name
                )
                ai.add_node(ifp_r, **ifp_r.model_dump())
                continue

            # check passes if for interface checks pass.
            ok = if_a_r.status == CheckStatus.PASS and if_b_r.status == CheckStatus.PASS

            ifp_r = TopologyCheckCabling(
                status="PASS" if ok else "FAIL", service=self.name, feature=feat.name
            )

            # -----------------------------------------------------------------
            # create the graph relationship between the service level check and
            # the device feature level checks.  Then create the relationship
            # betweent the service check and the top-level service node object.
            # -----------------------------------------------------------------

            ai.add_node(ifp_r, **ifp_r.model_dump())
            ai.add_edge(ifp_r, if_a_r, kind="r", service=self.name)
            ai.add_edge(ifp_r, if_b_r, kind="r", service=self.name)
            ai.add_edge(self, ifp_r, kind="r", service=self.name)

    def build_report(self, ai: "ServicesAnalyzer"):
        """
        The topology design service report will check the following items:
            (1) Are all the devices OK
            (2) Are all the interfaces OK
            (3) Are all the cabling OK
        """

        if devices_fail := [
            node
            for dev_obj in self.devices
            if (node := ai.nodes_map[dev_obj])["status"] == "FAIL"
        ]:
            self.status = "FAIL"

        if interfaces_fail := [
            node
            for if_obj in self.interfaces
            if (node := ai.nodes_map[if_obj])["status"] == "FAIL"
        ]:
            self.status = "FAIL"

        if cabling_fail := [
            node
            for edge in ai.nodes_map[self].out_edges()
            if edge["kind"] == "r"
            and edge.target_vertex["kind_type"] == "topology.cabling"
            if (node := edge.target_vertex)["status"] == "FAIL"
        ]:
            self.status = "FAIL"

        self.report = TopologyServiceReport(
            device_failures=devices_fail,
            interface_failures=interfaces_fail,
            cabling_failures=cabling_fail,
        )

    def show_report(self, console: Console):
        if not self.report:
            return

        did_pass = Text("PASS", Style(color="green"))
        did_fail = Text("FAIL", Style(color="red"))

        def condition(item):
            return did_pass if item else did_fail

        table = Table("Item", "Report", title=f"Service: {self.name} Topology Report")
        table.add_row("Service Status", condition(self.status == "PASS"))
        table.add_row("All devices ok?", condition(not self.report.device_failures))
        table.add_row(
            "All interfaces ok?", condition(not self.report.interface_failures)
        )
        table.add_row("All cabling ok?", condition(not self.report.cabling_failures))

        console.print(table)

        if not self.status == "PASS":
            console.print(self.build_features_report_table())
