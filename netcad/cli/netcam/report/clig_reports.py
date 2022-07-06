from typing import Tuple

from netcad.design import load_design
from netcad.reporting import DesginReporting
from netcad.cli.common_opts import opt_designs
from ..cli_netcam_main import cli


@cli.command(name="report")
@opt_designs()
def clig_reports(designs: Tuple[str]):
    """generate report"""

    design_name = designs[0]
    design = load_design(design_name=design_name)

    reporter = DesginReporting(design=design)
    reporter.build()
    reporter.run_reports()
    reporter.graph.write_graphml(f"{design.name}.graphml")
