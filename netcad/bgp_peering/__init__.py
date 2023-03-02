#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad import __version__ as plugin_version  # noqa

from .bgp_peering_design_service import (
    BgpPeeringDesignService,
    BgpPeeringDesignServiceLike,
)
from .bgp_peering_types import BGPSpeaker
from .bgp_neighbors import BGPPeerNeighbors
from . import cli


def plugin_init(config: dict):
    """unused by init autoloading for builtin-plugin modules"""
    pass
