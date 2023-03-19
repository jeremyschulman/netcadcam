#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
import click

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.console import Console
from rich.table import Table
from rich.pretty import Pretty

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.cli.cli_netcad_main import cli
from netcad.config import netcad_globals

# -----------------------------------------------------------------------------
# Exports (None)
# -----------------------------------------------------------------------------

__all__ = []


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@cli.command(name="list")
@click.option("--groups", "show_groups", is_flag=True, help="Should site-groups")
def cli_designs_list(show_groups: bool):
    """List available designs"""

    if show_groups is True:
        _show_design_groups_list()
        return

    designs = netcad_globals.g_netcad_designs
    console = Console()

    table = Table(
        "Name",
        "Description",
        "Config",
        "Notes",
        show_header=True,
        header_style="bold magenta",
        title="Available Designs",
        show_lines=True,
    )

    for name, design_decl in designs.items():
        if "group" in design_decl:
            continue

        notes = design_decl.get("notes")
        table.add_row(
            name,
            design_decl["description"],
            Pretty(design_decl.get("config") or ""),
            "\n".join(notes) if notes else "",
        )

    console.print("\n", table)


def _show_design_groups_list():
    designs = netcad_globals.g_netcad_designs
    console = Console()

    table = Table(
        "Group Name",
        "Description",
        "Sites",
        show_header=True,
        header_style="bold magenta",
        title="Available Designs",
        show_lines=True,
    )

    for name, design_decl in designs.items():
        if "group" not in design_decl:
            continue
        table.add_row(
            name, design_decl["description"], ", ".join(sorted(design_decl["group"]))
        )

    console.print("\n", table)
