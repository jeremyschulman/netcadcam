#  Copyright (c) 2025 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple, Sequence

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------
import click
from rich.console import Console
from rich.table import Table
from rich.text import Text, Style
from igraph import Graph

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.design import load_design
from netcad.services import ServicesAnalyzer, DesignService
from netcad.cli.common_opts import opt_designs
from ..cli_netcam_show import clig_show

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@clig_show.command(name="services")
@opt_designs()
@click.option("--service", "service_names", multiple=True, help="service name(s)")
@click.option("--brief", is_flag=True, help="show brief status only")
@click.option(
    "--all", "all_results", is_flag=True, help="show all results, not just failed"
)
def clig_reports(designs: Tuple[str], service_names: Sequence[str], **flags):
    """Show services reports"""

    design_name = designs[0]
    design = load_design(design_name=design_name)

    ai = ServicesAnalyzer(design=design)
    ai.graph = Graph.Read_GraphML(f"{design.name}.graphml")
    ai.build_reports(flags=flags)

    if not service_names:
        _show_all(ai, flags)
        return

    for name in service_names:
        if not (svc := design.services.get(name)):
            get_logger().error(f"Service {name} not found")
            continue

        _show_specific_service(ai, svc, flags)


def _show_all(ai, flags):
    console = Console()

    if not flags.get("brief"):
        ai.show_reports(console)
        return

    # -------------------------------------------------------------------------
    # brief mode
    # -------------------------------------------------------------------------

    table = Table("Service", "Status")
    for svc in ai.design.services.values():
        if svc.is_subservice and not flags.get("all_results"):
            continue

        # svc_rec = ai.db_find(table=db_tables.ServicesTable, name=svc.name)
        # svc_node = ai.graph.vs[svc_rec.node_id]
        # svc_status = svc_node["status"]

        table.add_row(
            svc.name,
            Text(svc.status, Style(color="red" if svc.status == "FAIL" else "green")),
        )

    console.print(table)


def _show_specific_service(ai: ServicesAnalyzer, service: DesignService, flags):
    if not flags.get("brief"):
        service.build_report(ai=ai, flags=flags)
        Console().print("\n\n", service.report.table)
        return

    # -------------------------------------------------------------------------
    # brief mode
    # -------------------------------------------------------------------------

    all_svcs = ai.service_graph(service)

    table = Table("Serice", "Status")
    for svc in all_svcs:
        table.add_row(
            svc.name,
            Text(
                svc.status,
                Style(color="red" if svc.status == "FAIL" else "green"),
            ),
        )

    Console().print(table)
