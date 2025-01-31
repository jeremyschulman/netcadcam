# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple, Sequence
import asyncio

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------
import click
from rich.console import Console
from rich.table import Table
from rich.text import Text, Style

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.design import load_design
from netcad.services import ServicesAnalyzer, DesignService
from netcad.cli.common_opts import opt_designs
from ..cli_netcam_main import cli

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@cli.group(name="services")
def clig_services():
    """Services commands"""
    pass


@clig_services.command(name="check")
@opt_designs()
@click.option("--service", "service_names", multiple=True, help="service name(s)")
@click.option("--brief", is_flag=True, help="show brief status only")
def clig_reports(designs: Tuple[str], service_names: Sequence[str], **flags):
    """generate report"""

    design_name = designs[0]
    design = load_design(design_name=design_name)

    ai = ServicesAnalyzer(design=design)
    ai.build()
    asyncio.run(ai.check())

    ai.graph.write_graphml(f"{design.name}.graphml")

    if not service_names:
        _show_all(ai, flags)
        return

    for name in service_names:
        if not (svc := design.services.get(name)):
            continue

        _show_specific_service(ai, svc, flags)


def _show_all(ai, flags):
    console = Console()

    ai.build_reports()

    if flags.get("brief"):
        table = Table("Service", "Status")
        for svc in ai.design.services.values():
            table.add_row(
                svc.name,
                Text(
                    svc.status, Style(color="red" if svc.status == "FAIL" else "green")
                ),
            )

        console.print(table)
        return

    ai.show_reports(console)


def _show_specific_service(ai, svc: DesignService, flags):
    svc.build_report(ai=ai)
    Console().print("\n\n", svc.report.table)
