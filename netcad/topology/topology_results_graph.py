# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------


from functools import singledispatchmethod

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.results_graph import ServiceResultsGrapher
from .checks.check_device_info import DeviceInformationCheck

from .checks.check_cabling_nei import InterfaceCablingCheck
from .checks.check_interfaces import InterfaceCheck, InterfaceExclusiveListCheck
from .checks.check_transceivers import TransceiverCheck, TransceiverExclusiveListCheck
from .checks.check_ipaddrs import IPInterfaceCheck, IPInterfaceExclusiveListCheck

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["TopologyResultsGrapher"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class TopologyResultsGrapher(ServiceResultsGrapher):
    def build_graph_edges(self):
        self.add_graph_edges_hubspkes(
            hub_check_type=DeviceInformationCheck,
            spoke_check_types=[
                InterfaceCheck,
                InterfaceCablingCheck,
                InterfaceExclusiveListCheck,
                TransceiverCheck,
                TransceiverExclusiveListCheck,
                IPInterfaceCheck,
                IPInterfaceExclusiveListCheck,
            ],
        )
        self._build_cable_peering()

    def _build_cable_peering(self):
        build = {
            dev: self.results_map[dev][InterfaceCablingCheck.check_type_()]
            for dev in self.devices
        }

        for dev, cables_rmap in build.items():
            for dev_ifname, cable_r in cables_rmap.items():

                rmt_iface = dev.interfaces[dev_ifname].cable_peer
                rmt_dev = rmt_iface.device
                rmt_cable_r = build[rmt_dev][rmt_iface.name]

                self.add_graph_edge(
                    source=cable_r,
                    target=rmt_cable_r,
                    status=self.edge_result_status(cable_r, rmt_cable_r),
                )
