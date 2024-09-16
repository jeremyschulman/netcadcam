#  Copyright (c) 2023 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

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


@clig_show_bgp.command(name="speakers")
@opt_designs()
@opt_devices()
def cli_show_bgp_routers(devices: Tuple[str], designs: Tuple[str]):
    """
    Show the BGP routers in the design(s)
    """

    # -------------------------------------------------------------------------
    # find all BGP features in the given design(s)
    # -------------------------------------------------------------------------

    design_insts = {load_design(dsn_name) for dsn_name in designs}

    if not (
        map_dev_bgp_spkrs := find_design_bgp_speakers(
            design_insts=design_insts, devices=devices
        )
    ):
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
