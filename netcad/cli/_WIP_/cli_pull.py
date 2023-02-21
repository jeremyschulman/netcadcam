#  Copyright (c) 2021-2022 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import asyncio
import os
from typing import Tuple

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.design import load_design
from netcad.config import Environment, netcad_globals

# -----------------------------------------------------------------------------
# Private Module Imports
# -----------------------------------------------------------------------------

from netcad.cli.common_opts import opt_designs
from netcad.cli.cli_netcad_main import cli

# -----------------------------------------------------------------------------
#
#                                   pull
#
# -----------------------------------------------------------------------------


@cli.group("pull")
def clig_pull():
    """pull design(s) artifact(s) from origins"""

    # disable the validation so that we can obtain information *about* the
    # design without attempting to build it when we import it.
    # TODO: perhaps consider a better approach than this env-var that breaks up
    #       the "load_design" into a two parts; because what it currently does
    #       is a "load" and "build".

    os.environ[Environment.NETCAD_NOVALIDATE] = "1"


# -----------------------------------------------------------------------------
#
#                              pull device-types
#
# -----------------------------------------------------------------------------


@clig_pull.command(name="device-types")
@opt_designs()
def cli_pull_device_types(designs: Tuple[str]):
    """pull device-type definitions from origins"""

    log = get_logger()
    origins = netcad_globals.g_netcad_origin_plugins_catalog
    errors = 0
    device_types = set()

    # obtain the unique list of device-type values across all deices in the User
    # provided set of designs.
    design_objs = set()

    for design_name in designs:
        design = load_design(design_name)
        for device in design.devices.values():
            design_objs.add(device.design)
            if not (pull_value := device.device_type or device.product_model):
                log.error(
                    f"Device missing device_type and product_model assignement: {device.name}"
                )
                errors += 1
                continue
            device_types.add(pull_value)

    log.debug(f"PULL device-types: {device_types}")

    for design in design_objs:
        for or_name, or_obj in origins.items():
            for svc in or_obj.services.values():
                asyncio.run(svc.plugin_origin_pull(design, services=["device-types"]))
