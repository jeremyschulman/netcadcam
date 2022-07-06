#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# Systeme Imports
# -----------------------------------------------------------------------------

from typing import Optional, TypeVar, Dict
from copy import copy

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from netcad.design.design_service import DesignService
from netcad.peering import PeeringPlanner

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .bgp_peering_types import BGPSpeaker, BGPPeeringEndpoint, BGPSpeakerName
from .checks import BgpNeighborsCheckCollection, BgpRoutersCheckCollection
from .bgp_peering_results_graph import BgpPeeringResultsGrapher

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["BgpPeeringDesignService", "BgpPeeringDesignServiceLike"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class BgpPeeringPlanner(PeeringPlanner[BGPSpeaker, BGPSpeakerName, BGPPeeringEndpoint]):
    pass


class BgpPeeringDesignService(DesignService, registry_name="bgp_peering"):
    """
    The VARP Design Service is specific to Arista EOS.
    """

    DEFAULT_SERVICE_NAME = "bgp_peering"

    CHECK_COLLECTIONS = [BgpRoutersCheckCollection, BgpNeighborsCheckCollection]
    REPORTER = BgpPeeringResultsGrapher

    def __init__(self, service_name: Optional[str] = None, **kwargs):
        super(BgpPeeringDesignService, self).__init__(
            service_name=service_name or self.DEFAULT_SERVICE_NAME, **kwargs
        )
        self.check_collections = copy(self.__class__.CHECK_COLLECTIONS)
        self.peering = BgpPeeringPlanner(name=service_name)

    def get_speaker(self, hostname: str, vrf: Optional[str] = None) -> "BGPSpeaker":
        """
        This function is used to retrieve the BGPSpeaker defined by the device
        hostname and VRF optional.

        The use of this function can be found in Jinja2 templates that need to
        obtain a BGP speaker in using these input types.

        Parameters
        ----------
        hostname: str
            The device hostname

        vrf: str, optonal
            The VRF name, or None.

        Returns
        -------
        BGPSpeaker as described
        """
        return self.speakers[BGPSpeakerName(hostname, vrf)]

    @property
    def speakers(self) -> Dict[BGPSpeakerName, BGPSpeaker]:
        return self.peering.peers

    def add_speakers(self, *speakers: BGPSpeaker):
        self.add_devices(*(spkr.device for spkr in speakers))
        self.peering.add_peers(*speakers)
        return self

    def validate(self):
        pass

    def build(self):
        self.peering.build()


BgpPeeringDesignServiceLike = TypeVar(
    "BgpPeeringDesignServiceLike", BgpPeeringDesignService, DesignService
)
