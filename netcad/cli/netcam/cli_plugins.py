#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from rich.console import Console
from rich.table import Table
from rich.pretty import Pretty

from .cli_netcam_main import cli


from netcad.config import netcad_globals


@cli.group("plugins")
def clig_netcam_plugins():
    """netcam plugin subcommands ..."""
    pass


@clig_netcam_plugins.command("list")
def cli_netcam_plugins_list():
    table = Table("Name", "Description", "Package", "Supports", show_header=True)

    for pg_obj in netcad_globals.g_netcam_plugins:
        table.add_row(
            pg_obj.name,
            pg_obj.plugin_description or "",
            pg_obj.package,
            Pretty(pg_obj.config["supports"]),
        )

    Console().print(table)
