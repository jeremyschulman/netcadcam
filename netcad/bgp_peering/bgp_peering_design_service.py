#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# Systeme Imports
# -----------------------------------------------------------------------------

from typing import Optional, TypeVar
from copy import copy

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from netcad.design.design_service import DesignService
from netcad.peering import PeeringPlanner

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .bgp_peering_types import BGPSpeaker, BGPPeeringEndpoint
from .checks import BgpNeighborsCheckCollection

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["BgpPeeringDesignService", "BgpPeeringDesignServiceLike"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class BgpPeeringPlanner(PeeringPlanner[BGPSpeaker, BGPPeeringEndpoint]):
    pass


class BgpPeeringDesignService(DesignService, registry_name="bgp_peering"):
    """
    The VARP Design Service is specific to Arista EOS.
    """

    DEFAULT_SERVICE_NAME = "bgp_peering"
    CHECK_COLLECTIONS = [BgpNeighborsCheckCollection]

    def __init__(self, service_name: Optional[str] = None, **kwargs):
        super(BgpPeeringDesignService, self).__init__(
            service_name=service_name or self.DEFAULT_SERVICE_NAME, **kwargs
        )
        self.check_collections = copy(self.__class__.CHECK_COLLECTIONS)
        self.peering = BgpPeeringPlanner(name=service_name)

    @property
    def speakers(self):
        return self.peering.peers

    def get_speaker(self, hostname: str) -> BGPSpeaker:
        return self.peering.get_peer(hostname)

    def add_speakers(self, *speakers: BGPSpeaker):
        self.peering.add_peers(*speakers)
        return self

    def validate(self):
        pass

    def build(self):
        self.peering.build()


BgpPeeringDesignServiceLike = TypeVar(
    "BgpPeeringDesignServiceLike", BgpPeeringDesignService, DesignService
)
