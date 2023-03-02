#  Copyright (c) 2023 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple
from collections import defaultdict

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.table import Table
from rich.console import Console

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.design import load_design
from netcad.cli.common_opts import opt_devices, opt_designs

from ..bgp_peering_design_service import BgpPeeringDesignService
from .cli_show_bgp import clig_show_bgp

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@clig_show_bgp.command(name="speakers")
@opt_designs()
@opt_devices()
def cli_show_bgp_routers(devices: Tuple[str], designs: Tuple[str]):
    """
    Show the BGP routers in the design(s)
    """

    log = get_logger()

    # -------------------------------------------------------------------------
    # find all BGP services in the given design(s)
    # -------------------------------------------------------------------------

    design_insts = {load_design(dsn_name) for dsn_name in designs}
    if not design_insts:
        log.error("No designs found")
        return

    bgp_svc_insts: set[BgpPeeringDesignService] = set()
    for design in design_insts:
        bgp_svc_insts.update(design.services_of(BgpPeeringDesignService))

    if not bgp_svc_insts:
        log.error("No BGP services found")
        return

    # -------------------------------------------------------------------------
    # create a map of device-name to a list of (BGP-SVC, BGP-SPKR) so that the
    # report is organized by device.  If the User provided a list of `devices`
    # to filter against, ensure only those devices end up in the map.
    # -------------------------------------------------------------------------

    map_dev_bgp_spkrs = defaultdict(list)
    for bgp_svc in bgp_svc_insts:
        for spkr in bgp_svc.speakers.values():
            hostname = spkr.device.name
            if devices and hostname not in devices:
                continue
            map_dev_bgp_spkrs[hostname].append(spkr)

    if not map_dev_bgp_spkrs:
        log.error("No devices found in BGP services")
        return

    display_device_routers(map_dev_bgp_spkrs)


def display_device_routers(map_dev_bgp_spkrs):
    """
    Using the compiled mapping of BGP speakers create a single table containing
    the information for the User.
    """
    console = Console()
    table = Table(
        "Device",
        "Router-ID",
        "ASN",
        "VRF",
        "#Neighbors",
        title_justify="left",
        show_header=True,
        show_lines=True,
        header_style="bold magenta",
    )

    for hostname, bgp_spkrs in map_dev_bgp_spkrs.items():
        for spkr in bgp_spkrs:
            table.add_row(
                hostname,
                str(spkr.router_id),
                str(spkr.asn),
                spkr.vrf or "default",
                str(len(spkr.neighbors)),
            )

    table.title = f"{len(table.rows)} BGP speakers"
    console.print("\n", table)
