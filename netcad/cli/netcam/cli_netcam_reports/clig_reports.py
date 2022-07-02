from typing import Tuple

from netcad.design import load_design
from netcad.design import DesignCheckResultsGraph
from netcad.cli.common_opts import opt_designs, opt_design_services
from ..cli_netcam_main import cli


@cli.command(name="report")
@opt_designs()
@opt_design_services()
def clig_reports(designs: Tuple[str], services: Tuple[str]):
    """generate report"""

    design_name = designs[0]
    design = load_design(design_name=design_name)

    drg = DesignCheckResultsGraph(design=design)

    drg.build(services=services)
