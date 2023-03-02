#  Copyright (c) 2023 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple
from operator import attrgetter

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.table import Table, Text, Style
from rich.console import Console

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.cli.device_inventory import get_devices_from_designs
from netcad.cli.common_opts import opt_devices, opt_designs

from .cli_show_bgp import clig_show_bgp

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

    log = get_logger()

    if not (device_objs := get_devices_from_designs(designs, include_devices=devices)):
        log.error("No devices located in the given designs")
        return

    breakpoint()
