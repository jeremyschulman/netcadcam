from netcad.init import loader
from .clig_design import clig_design


# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import click
from rich.console import Console
from rich.table import Table


@clig_design.command(name="list")
def cli_designs_list():
    """List available designs"""

    designs = loader.import_designs_packages()
    console = Console()

    table = Table(
        show_header=True, header_style="bold magenta", title="Available Designs"
    )
    table.add_column("Name")
    table.add_column("Description")

    for name, details in designs.items():
        table.add_row(name, details["description"])

    console.print("\n", table)
