#  Copyright (c) 2023 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Sequence, Dict, List, Set
from collections import defaultdict


# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.design import Design
from netcad.logger import get_logger

from ..bgp_peering_design_service import BgpPeeringDesignService
from ..bgp_peering_types import BGPSpeaker


def find_design_bgp_speakers(
    design_insts: Set[Design], devices: Sequence[str]
) -> Dict[str, List[BGPSpeaker]] | None:
    log = get_logger()

    bgp_svc_insts = set()
    for design in design_insts:
        bgp_svc_insts.update(design.services_of(BgpPeeringDesignService))

    if not bgp_svc_insts:
        log.error("No BGP features found")
        return None

    # -------------------------------------------------------------------------
    # create a map of device-name to a list of (BGP-SVC, BGP-SPKR) so that the
    # report is organized by device.  If the User provided a list of `devices`
    # to filter against, ensure only those devices end up in the map.
    # -------------------------------------------------------------------------

    map_dev_bgp_spkrs = defaultdict(list)
    bgp_svc: BgpPeeringDesignService

    for bgp_svc in bgp_svc_insts:
        for spkr in bgp_svc.speakers.values():
            hostname = spkr.device.name
            if devices and hostname not in devices:
                continue
            map_dev_bgp_spkrs[hostname].append(spkr)

    if not map_dev_bgp_spkrs:
        log.error("No devices found in BGP features")
        return None

    return map_dev_bgp_spkrs
