# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Callable, Literal

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, ConfigDict

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
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
    model_config = ConfigDict(arbitrary_types_allowed=True)

    topology_feature: TopologyDesignFeature
    match_interface_profile: Callable


class TopologyCheckCabling(BaseModel):
    service: str
    feature: str
    check_type: str = "topology.cabling"
    kind: str = "r"
    status: Literal["PASS", "FAIL"]

    def __hash__(self):
        return id(self)


class TopologyService(DesignService):
    CHECKS = [TopologyCheckCabling]

    def __init__(self, *vargs, config: TopologyServiceConfig, **kwargs):
        super().__init__(*vargs, **kwargs)
        self.config = config
        self.devices: set[Device] = None
        self.interfaces: set[DeviceInterface] = None

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

        if not self.match_interfaces():
            get_logger().error(f"No interfaces found for service: {self.name}")
            return

        # -----------------------------------------------------------------------------
        # build the device -> interface design graph.  Initialize the status
        # value for each design node to "PASS".  This status will be updated
        # should the analyzer find that any related checks fail.
        # -----------------------------------------------------------------------------

        for dev_obj in self.devices:
            ai.add_node(dev_obj, device=dev_obj.name, kind="d", status="PASS")
            ai.add_edge(self, dev_obj, kind="d")

        for if_obj in self.interfaces:
            ai.add_node(
                if_obj,
                device=if_obj.device.name,
                if_name=if_obj.name,
                kind="d",
                status="PASS",
            )
            ai.add_edge(if_obj.device, if_obj, kind="d")
            ai.add_edge(self, if_obj, kind="d")

    def build_results_graph(self, ai: ServicesAnalyzer):
        devinfo_checks_map = {
            dev_obj: ai.results_map[dev_obj][DeviceInformationCheck.check_type_()][
                dev_obj.name
            ]
            for dev_obj in self.devices
        }

        # -----------------------------------------------------------------------------
        # associate the check result to the device design object.
        # -----------------------------------------------------------------------------

        for dev_obj, check_r_obj in devinfo_checks_map.items():
            ai.add_edge(dev_obj, check_r_obj, kind="r")
            ai.add_edge(check_r_obj, dev_obj, kind="d")

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

                ai.nodes_map[if_check_obj]["service"] = self.name
                ai.add_edge(if_obj, if_check_obj, kind="r")
                ai.add_edge(if_check_obj, if_obj, kind="d")

    async def check(self, ai: ServicesAnalyzer):
        # use the cabling from the topology feature to create the "topology
        # interface peer check".

        feat = self.config.topology_feature

        # first step is to filter the list of cabling to only those with
        # interfaces matching the topology service interfaces set and are not
        # virtual interfaces, like port-channels.

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

            ok = if_a_r.status == CheckStatus.PASS and if_b_r.status == CheckStatus.PASS

            ifp_r = TopologyCheckCabling(
                status="PASS" if ok else "FAIL", service=self.name, feature=feat.name
            )

            # create the graph relationship between the service level check and
            # the device feature level checks.

            ai.add_node(ifp_r, **ifp_r.model_dump())
            ai.add_edge(ifp_r, if_a_r, kind="r")
            ai.add_edge(ifp_r, if_b_r, kind="r")
