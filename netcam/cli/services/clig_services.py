# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple
import asyncio

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.table import Table
from rich.pretty import Pretty
from rich.console import Console

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.design import load_design
from netcad.services import ServicesAnalyzer
from netcad.cli.common_opts import opt_designs
from netcad.services import DesignService
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

    console = Console()

    for svc_obj in design.services.values():
        if len(svc_obj.failed):
            console.print(build_service_report_table(svc_obj))

        else:
            console.print(f"Service {svc_obj.name}:  PASS")

    ai.graph.write_graphml(f"{design.name}.graphml")


def build_service_report_table(svc: DesignService) -> Table:
    table = Table(
        "Device",
        "Check Type",
        "Check ID",
        "Status",
        title=f"Service: {svc.name}",
        title_justify="left",
    )

    for check in sorted(svc.failed, key=lambda i: i.device):
        fail_logs = [log for log in check.logs.root if log[0] == "FAIL"]
        device = check.device
        check_id = check.check_id
        table.add_row(device, check.check.check_type, check_id, Pretty(fail_logs))

    return table
