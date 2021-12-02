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
        show_header=True, header_style="bold magenta", title="Available Designs"
    )
    table.add_column("Name")
    table.add_column("Description")

    for name, details in designs.items():
        table.add_row(name, details["description"])

    console.print("\n", table)
