# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple
import asyncio

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.console import Console

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.design import load_design
from netcad.services import ServicesAnalyzer
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
def clig_reports(designs: Tuple[str]):
    """generate report"""

    design_name = designs[0]
    design = load_design(design_name=design_name)

    ai = ServicesAnalyzer(design=design)
    ai.build()

    asyncio.run(ai.check())

    ai.show_report(console=Console())
    ai.graph.write_graphml(f"{design.name}.graphml")
