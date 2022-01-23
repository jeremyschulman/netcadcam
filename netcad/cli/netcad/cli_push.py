#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import asyncio
from typing import Tuple

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.init.init_netcad_origin_plugins import init_netcad_origin_plugins
from netcad.design import load_design

# -----------------------------------------------------------------------------
# Private Module Imports
# -----------------------------------------------------------------------------

from ..common_opts import opt_designs
from .cli_netcad_main import cli

# -----------------------------------------------------------------------------
#
#                                   push
#
# -----------------------------------------------------------------------------


@cli.command("push")
@opt_designs()
def cli_push(designs: Tuple[str]):
    """push design(s) to origin(s) ..."""

    log = get_logger()

    origins = init_netcad_origin_plugins()

    for design_name in designs:
        design = load_design(design_name)
        for or_name, or_obj in origins.items():
            for svc in or_obj.services.values():
                log.info(f"PUSH: {design_name} -> {or_name}.{svc.name}")
                asyncio.run(svc.plugin_origin_push(design))
