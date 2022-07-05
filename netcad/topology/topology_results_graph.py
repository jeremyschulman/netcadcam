# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.reporting import ServiceReporting
from netcad.checks import CheckStatus

from .checks.check_device_info import DeviceInformationCheck
from .checks.check_cabling_nei import InterfaceCablingCheck, InterfaceCablingCheckResult
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


class TopologyResultsGrapher(ServiceReporting):
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

        # create a map of devies to their cabling check results dictionary. the
        # key of that dict (check-id) is the interface name, and the values are
        # the specific result instances.  This build map will be used to
        # crosswise lookup peering cabling results.

        build = {
            dev: self.results_map[dev][InterfaceCablingCheck.check_type_()]
            for dev in self.devices
        }

        cable_r: InterfaceCablingCheckResult

        for dev, cables_rmap in build.items():
            for dev_ifname, cable_r in cables_rmap.items():

                # if the cable check failed, then do not create the
                # peering edge.

                if cable_r.status == CheckStatus.FAIL:
                    continue

                # otherwise we have a good cable check, and we can form the
                # peering edge in the graph.

                rmt_iface = dev.interfaces[dev_ifname].cable_peer
                rmt_dev = rmt_iface.device
                rmt_cable_r = build[rmt_dev][rmt_iface.name]

                self.add_graph_edge(
                    source=cable_r, target=rmt_cable_r, status=cable_r.status
                )
