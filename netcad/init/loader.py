# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import asyncio
from typing import Optional, AnyStr, Dict
import sys
import os
from importlib import import_module

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import netcad_globals
from netcad.config.envvars import Environment

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def import_designs_packages(root_path: Optional[AnyStr] = None) -> Dict:
    # Add the User's project directory for python import path.

    sys.path.insert(0, root_path or os.environ[Environment.NETCAD_PROJECTDIR])

    if not (design_configs := netcad_globals.g_config.get("design")):
        raise RuntimeError(
            f'Missing "design" definitions in config-file: {netcad_globals.g_netcad_config_file}'
        )

    for name, details in design_configs.items():
        pkg = details["package"]
        try:
            details["module"] = import_module(pkg)

        except ImportError as exc:
            raise RuntimeError(f"Unable to load network module: {exc.args[0]}")

    netcad_globals.g_netcad_designs = design_configs
    return design_configs


def run_designs(designs: Dict):

    design_tasks = [
        mod.design()
        for design_details in designs.values()
        if (
            hasattr((mod := design_details["module"]), "design")
            and asyncio.iscoroutinefunction(mod.design)
        )
    ]

    async def run_design(tasks):
        await asyncio.gather(tasks)

    if design_tasks:
        asyncio.run(run_design(*design_tasks))
