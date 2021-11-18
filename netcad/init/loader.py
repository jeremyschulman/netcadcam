# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import asyncio
from typing import Dict
from importlib import import_module

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import netcad_globals

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def import_designs_packages() -> Dict:

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


def load_design(design_name: str) -> Dict:
    """
    This function loads the specific design by importing the related package and
    running the `design` method.

    Parameters
    ----------
    design_name:
        The name of design as defined by the User in the netcad configuraiton
        file.

    Returns
    -------
    The design informational instance.
    """

    if not (design_config := netcad_globals.g_netcad_designs.get(design_name)):
        raise RuntimeError(
            f'Missing design "{design_name}" definitions in config-file: {netcad_globals.g_netcad_config_file}'
        )

    pkg = design_config["package"]
    try:
        design_config["module"] = import_module(pkg)

    except ImportError as exc:
        raise RuntimeError(f"Unable to load network module: {exc.args[0]}")

    # if the design package contains a "design" async function, then execute
    # that now.

    if hasattr(
        (mod := design_config["module"]), "design"
    ) and asyncio.iscoroutinefunction(mod.design):
        asyncio.run(mod.design())

    return design_config


# -----------------------------------------------------------------------------


def run_designs(designs: Dict):

    design_tasks = [
        mod.design()
        for design_details in designs.values()
        if (
            hasattr((mod := design_details["module"]), "design")
            and asyncio.iscoroutinefunction(mod.design)
        )
    ]

    async def run_design():
        await asyncio.gather(*design_tasks)

    if design_tasks:
        asyncio.run(run_design())
