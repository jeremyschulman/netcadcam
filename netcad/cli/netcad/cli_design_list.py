# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.console import Console
from rich.table import Table

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.cli.netcad.cli_netcad_main import cli
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
def cli_designs_list():
    """List available designs"""

    designs = netcad_globals.g_netcad_designs
    console = Console()

    table = Table(
        "Name",
        "Description",
        "Group",
        show_header=True,
        header_style="bold magenta",
        title="Available Designs",
    )

    for name, details in designs.items():
        group = ", ".join(details.get("group", ""))
        table.add_row(name, details["description"], group)

    console.print("\n", table)
