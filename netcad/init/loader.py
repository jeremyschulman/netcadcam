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
            from_pkg, design_mod = pkg.rsplit(".", 1)
            details["module"] = getattr(import_module(from_pkg), design_mod)

        except ImportError as exc:
            raise RuntimeError(f"Unable to load network module: {exc.args[0]}")

    netcad_globals.g_netcad_designs = design_configs
    return design_configs


def import_design(pkg_name: str):

    # try to import the package name as given.  If the package name as given is
    # not found then we will try another approach.  The package name could be
    # given as an import reference within another file, for example "import foo
    # as bar" and the package name as given references "bar".  In this case the
    # direct import_module will fail resulting in a ModuleNotFound Error.

    try:
        return import_module(pkg_name)
    except ModuleNotFoundError:
        pass

    # Try splitting the package as given into the from package and then an
    # attribute within that module.  This will handle the case described above.

    from_pkg, design_name = pkg_name.rsplit(".", 1)
    return getattr(import_module(from_pkg), design_name)


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

    pkg_name = design_config["package"]

    try:
        design_mod = import_design(pkg_name)

    except Exception as exc:
        rt_exc = RuntimeError(
            f'Failed to import design "{design_name}" from package: "{pkg_name}";\n'
            f"Exception: {str(exc)}",
        )
        rt_exc.__traceback__ = exc.__traceback__
        raise rt_exc

    if not design_mod:
        raise RuntimeError(f'Failed to import design "{design_name}"')

    if hasattr(design_mod, "design") and asyncio.iscoroutinefunction(design_mod.design):
        asyncio.run(design_mod.design())

    design_config["module"] = design_mod
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
