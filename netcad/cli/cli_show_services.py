#  Copyright (c) 2025 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Sequence

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.table import Table
from rich.console import Console

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.design import Design, load_design
from netcad.logger import get_logger
from netcad.cli.common_opts import opt_designs


from .clig_netcad_show import clig_design_show as cli

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@cli.command(name="services")
@opt_designs()
def cli_show_services(designs: Sequence[str]):
    designs = {
        design_name: load_design(design_name=design_name) for design_name in designs
    }

    if not designs:
        get_logger().error("No designs found by those name(s)")
        return

    for design in designs.values():
        show_design_services(design)


def show_design_services(design: Design):
    table = Table(
        "Service",
        "Kind",
        show_header=True,
        header_style="bold magenta",
        title_justify="left",
        show_lines=True,
        title=f"Design: '{design.name}'",
    )

    service_names = sorted(design.services)

    for feat_name in service_names:
        feat = design.services[feat_name]
        kind = feat.__class__.__name__
        table.add_row(feat.name, kind)

    Console().print(table)
