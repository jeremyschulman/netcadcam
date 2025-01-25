from typing import Tuple
import asyncio

from netcad.design import load_design
from netcad.services import ServicesAnalyzer
from netcad.cli.common_opts import opt_designs
from ..cli_netcam_main import cli


@cli.command(name="report")
@opt_designs()
def clig_reports(designs: Tuple[str]):
    """generate report"""

    design_name = designs[0]
    design = load_design(design_name=design_name)

    ai = ServicesAnalyzer(design=design)
    ai.build()
    asyncio.run(ai.check())

    ai.graph.write_graphml(f"{design.name}.graphml")
