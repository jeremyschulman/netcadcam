#  Copyright (c) 2022 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple
from itertools import filterfalse

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.table import Table
from rich.console import Console

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import HostDevice
from netcad.design import Design, load_design
from netcad.logger import get_logger
from netcad.cli.common_opts import opt_designs


from .clig_netcad_show import clig_design_show as cli

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@cli.command(name="services")
@opt_designs()
def cli_show_services(designs: Tuple[str]):
    """
    show services in design

    This command will show the design services, service checks, and
    associated devices in the given design(s).
    """

    designs = {
        design_name: load_design(design_name=design_name) for design_name in designs
    }

    if not designs:
        get_logger().error("No designs found by those name(s)")
        return

    for design in designs.values():
        show_design_services(design)


def show_design_services(design: Design):
    table = Table(
        "Service Name",
        "Kind",
        "Checks",
        "Devices",
        show_header=True,
        header_style="bold magenta",
        title_justify="left",
        show_lines=True,
        title=f"Design: '{design.name}'",
    )

    service_names = sorted(design.services)

    for service_name in service_names:
        service = design.services[service_name]

        devices = sorted(
            filterfalse(lambda _d: isinstance(_d, HostDevice), service.devices)
        )

        if not devices:
            continue

        device_svc = devices[0].services[service.name]
        checks = sorted(check.get_name() for check in device_svc.check_collections)

        kind = service.__class__.__name__

        table.add_row(
            service.name, kind, ", ".join(checks), ", ".join([d.name for d in devices])
        )

    Console().print(table)
