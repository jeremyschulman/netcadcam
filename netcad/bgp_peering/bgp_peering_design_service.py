#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# Systeme Imports
# -----------------------------------------------------------------------------

from typing import Optional, TypeVar

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.design.design_service import DesignService
from ..peering import PeeringPlanner, PeeringEndpoint

from .bgp_neighbors import BGPPeerNeighbors


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["BgpPeeringDesignService", "BgpPeeringDesignServiceLike"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class BgpPeeringDesignService(DesignService, registry_name="bgp_peering"):
    """
    The VARP Design Service is specific to Arista EOS.
    """

    DEFAULT_SERVICE_NAME = "bgp_peering"

    CHECK_COLLECTIONS = []

    def __init__(self, service_name: Optional[str] = None, **kwargs):
        super(BgpPeeringDesignService, self).__init__(
            service_name=service_name or self.DEFAULT_SERVICE_NAME, **kwargs
        )
        self.peering = PeeringPlanner(name=service_name)

    def add_neighbors(self, *neighbors: BGPPeerNeighbors):
        for nei in neighbors:
            for nei_peer in nei.speakers:
                self.peering.add_endpoint(
                    peering_id=nei.peer_id,
                    peer_endpoint=PeeringEndpoint(enabled=nei.enabled, peer=nei_peer),
                )

    def validate(self):
        pass

    def build(self):
        pass


BgpPeeringDesignServiceLike = TypeVar(
    "BgpPeeringDesignServiceLike", BgpPeeringDesignService, DesignService
)
