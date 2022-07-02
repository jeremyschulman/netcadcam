from typing import Tuple

from netcad.design import load_design

from netcad.design_results_graph import DesignServiceResultsGraph


from netcad.cli.common_opts import opt_designs, opt_design_services
from ..cli_netcam_main import cli


@cli.command(name="report")
@opt_designs()
@opt_design_services()
def clig_reports(designs: Tuple[str], services: Tuple[str]):
    """generate report"""

    design_name = designs[0]
    design = load_design(design_name=design_name)

    svcs = design.services.values()
    if services:
        svcs = filter(lambda s: s.name in services, svcs)

    for svc in svcs:
        drg = DesignServiceResultsGraph(design=design, service=svc)
        drg.build_graph_nodes()
