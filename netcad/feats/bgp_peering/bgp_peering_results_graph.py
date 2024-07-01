# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.reporting import ServiceReporting
from .checks.bgp_check_routers import BgpRouterCheck
from .checks.check_bgp_neighbors import BgpNeighborCheck, BgpNeighborCheckResult

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["BgpPeeringResultsGrapher"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class BgpPeeringResultsGrapher(ServiceReporting):
    def build_graph_edges(self):
        self.add_graph_edges_hubspkes(
            hub_check_type=BgpRouterCheck, spoke_check_types=[BgpNeighborCheck]
        )
        self._build_bgp_neighbor_peering()

    def _build_bgp_neighbor_peering(self):
        # the check-id for the bgp neighbor check is the IP address of the
        # local interface used to establish the BGP peering session.

        build = {
            dev: self.results_map[dev][BgpNeighborCheck.check_type_()]
            for dev in self.devices
        }

        # the check params for each neightbor result include the expected
        # neighbor device name and IP address.  So we can crosswise look up the
        # relationship in the above build map.

        nei_r: BgpNeighborCheckResult
        for dev, dev_neis_rmap in build.items():
            for if_ipaddr, nei_r in dev_neis_rmap.items():
                # even if the check failed, create the edge because we want to
                # represent the design expectation visually.  We will set the
                # status of the edge so that the value can be filtered against
                # in graph analysis.

                rmt_dev_name = nei_r.check.check_params.nei_name
                rmt_nei_ip = nei_r.check.check_params.via_ip

                rmt_dev = self.design.devices[rmt_dev_name]
                rmt_nei_r = build[rmt_dev][rmt_nei_ip]

                self.add_graph_edge(source=nei_r, target=rmt_nei_r, status=nei_r.status)
