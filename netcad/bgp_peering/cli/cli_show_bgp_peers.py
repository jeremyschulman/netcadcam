# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.table import Table
from rich.console import Console

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.design import load_design
from netcad.cli.common_opts import opt_devices, opt_designs
from .cli_show_bgp import clig_show_bgp
from .bgp_design_spkrs import find_design_bgp_speakers

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@clig_show_bgp.command(name="peers")
@opt_designs()
@opt_devices()
def cli_show_bgp_peers(devices: Tuple[str], designs: Tuple[str]):
    """
    Show the BGP neighbor peers in the design(s)
    """

    # -------------------------------------------------------------------------
    # find all BGP services in the given design(s)
    # -------------------------------------------------------------------------

    design_insts = {load_design(dsn_name) for dsn_name in designs}

    if not (
        map_dev_bgp_spkrs := find_design_bgp_speakers(
            design_insts=design_insts, devices=devices
        )
    ):
        return

    display_bgp_peers(map_dev_bgp_spkrs)


def display_bgp_peers(map_dev_bgp_spkrs):
    """
    Using the compiled mapping of BGP speakers create a single table containing
    the information for the User.
    """
    console = Console()
    table = Table(
        # Local information
        "Device",
        "VRF",
        "ASN",
        "Router-ID",
        "Via-IP",
        "BGP Type",
        # Peering information
        "Via-IP",
        "Router-ID",
        "ASN",
        "VRF",
        "Device",
        title_justify="left",
        show_header=True,
        show_lines=True,
        header_style="bold magenta",
    )

    # the BGP peers share a common ID value.  We will use this value to ensure
    # we only show one instance of the peering relationship.

    known_peer_ids = set()

    for hostname, bgp_spkrs in map_dev_bgp_spkrs.items():
        for spkr in bgp_spkrs:
            for nei in spkr.neighbors:
                # if we're already seen this BGP peering relationship then skip
                # it so we do not have duplicate A <> B,  B <> A table entries.

                if nei.peer_id in known_peer_ids:
                    continue

                known_peer_ids.add(nei.peer_id)

                lcl_spkr = nei.speaker
                rmt_spkr = nei.remote.speaker

                table.add_row(
                    hostname,
                    lcl_spkr.vrf or "default",
                    str(lcl_spkr.asn),
                    str(lcl_spkr.router_id),
                    str(nei.via_ip),
                    nei.bgp_type,
                    str(nei.remote.via_ip),
                    str(rmt_spkr.router_id),
                    str(rmt_spkr.asn),
                    rmt_spkr.vrf or "default",
                    rmt_spkr.device.name,
                )

    table.title = f"{len(table.rows)} BGP peers"
    console.print("\n", table)
