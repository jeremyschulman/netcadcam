# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Callable, ClassVar, Any

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, ConfigDict
from rich.console import Console

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
        self._build_results_deviceinfo(ai)
        self._build_results_interfaces(ai)

    def _build_results_deviceinfo(self, ai: ServicesAnalyzer):
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

    def _build_results_interfaces(self, ai: ServicesAnalyzer):
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

    # -------------------------------------------------------------------------
    #
    #                             Checks
    #
    # -------------------------------------------------------------------------

    async def check(self, ai: ServicesAnalyzer):
        """
        This function is used to generate service-level checkss.  The only
        check for the topology service is to check whether the cabline between
        interfaces are correct.
        """

        self._check_devices(ai)
        self._check_interfaces(ai)
        self._check_cabling(ai)

    def _check_devices(self, ai: ServicesAnalyzer):
        pass

    def _check_interfaces(self, ai: ServicesAnalyzer):
        pass

    def _check_cabling(self, ai: ServicesAnalyzer):
        # create the top level cabling check node that will be the parent to
        # each of the individual interface cabling checks.

        top_node = TopologyCheckCabling()
        ai.add_node(top_node, kind="r", service=self.name)
        ai.add_edge(self, top_node, kind="r", service=self.name)

        # -----------------------------------------------------------------------------
        # first step is to filter the list of cabling to only those with
        # interfaces matching the topology service interfaces set and are not
        # virtual interfaces, like port-channels.
        # -----------------------------------------------------------------------------

        feat = self.config.topology_feature

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
            # TODO: not sure the checks are missing, the but measurement could
            #       be missing.  May need to account for that scenario.

            if_a_r = ai.results_map[if_a.device][if_cable_check].get(if_a.name)
            if_b_r = ai.results_map[if_b.device][if_cable_check].get(if_b.name)

            if not (if_a_r and if_b_r):
                ifp_r = TopologyCheckCabling(ok=False, msrd={"error": "Missing checks"})
                ai.add_node(
                    ifp_r, kind="r", check_type=ifp_r.check_type, service=self.name
                )
                ai.add_edge(top_node, ifp_r, kind="r", service=self.name)
                continue

            # check passes if for interface checks pass.

            if not (
                ok := if_a_r.status == CheckStatus.PASS
                and if_b_r.status == CheckStatus.PASS
            ):
                top_node.ok = False

            ifp_r = TopologyCheckCabling(ok=ok)

            # -----------------------------------------------------------------
            # create the graph relationship between the service level check and
            # the device feature level checks.  Then create the relationship
            # betweent the service check and the top-level service node object.
            # -----------------------------------------------------------------

            ai.add_node(ifp_r, kind="r", check_type=ifp_r.check_type, service=self.name)
            ai.add_edge(ifp_r, if_a_r, kind="r", service=self.name)
            ai.add_edge(ifp_r, if_b_r, kind="r", service=self.name)
            ai.add_edge(top_node, ifp_r, kind="r", service=self.name)

    def show_report(self, ai: ServicesAnalyzer, console: Console):
        svc_node = ai.nodes_map[self]

        check_nodes = {
            t["name"].__class__: ai.nodes_map.inv[t]
            for t in [e.target_vertex for e in svc_node.out_edges() if e["kind"] == "r"]
        }

        report = DesignServiceReport(title=f"Topology Service Report: {self.name}")
        # report.add("All devices OK", not self.report.device_failures)
        # report.add("All interfaces OK", not self.report.device_failures)

        svc_cable_check = check_nodes[TopologyCheckCabling]
        report.add("All cabling OK", svc_cable_check)

        # if not self.status == "PASS":
        if True:
            report.add(
                "Feature Issues", False, details=self.build_features_report_table()
            )

        console.print(report.table)
