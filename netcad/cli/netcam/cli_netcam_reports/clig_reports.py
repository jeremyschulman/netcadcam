from typing import Tuple

from netcad.design import load_design

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

    svc_graphs = list()

    for svc in svcs:
        svc_graphs.append(svc.results_graph())

    for gr in svc_graphs:
        gr.build_graph_nodes()

    for gr in svc_graphs:
        gr.build_graph_edges()
