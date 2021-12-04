# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import asyncio
from typing import Dict
from types import ModuleType
from importlib import import_module
import inspect

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import netcad_globals

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def netcad_import_package(pkg_name: str) -> ModuleType:
    """
    This function will import the module as defined by the `pkg_name` value.
    This name originates in the netcad configuration file and could be one
    cases.  The first case is the package name referrs to an actual module file.
    The second case is that the package name referrs to an attribute within a
    package module.

    Parameters
    ----------
    pkg_name:
        The package name, as providing in standard Python dotted notation.

    Returns
    -------
    The module loaded.
    """

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
    executes the `design` function.

    Parameters
    ----------
    design_name: str
        The name of design as defined by the User in the netcad configuraiton
        file.  For example, if the configuration file contained a toplevel entry
        "[design.foobaz]" then the `design_name` is "foobaz".

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
        design_mod = netcad_import_package(pkg_name)

    # If there is any exception during the importing of the module, that is a
    # coding error by the Developer, then we need to raise that so the CLI
    # output will dispaly the information to the User with the hopes that the
    # information will aid in debugging.

    except Exception as exc:
        rt_exc = RuntimeError(
            f'Failed to import design "{design_name}" from package: "{pkg_name}";\n'
            f"Exception: {str(exc)}",
        )
        rt_exc.__traceback__ = exc.__traceback__
        raise rt_exc

    if not design_mod:
        raise RuntimeError(f'Failed to import design "{design_name}"')

    # The design function is expected to be async.
    # TODO: log a warning if one is not found?  Is it possible that a design
    #       module does not have a "design" method?  This is unlikely and possibly
    #       should raise a RuntimeError if the 'design' function is missing.

    if hasattr(design_mod, "design") and asyncio.iscoroutinefunction(design_mod.design):
        design_coro = design_mod.design
        sig = inspect.signature(design_coro)
        run_coro = (
            design_coro(design_name, design_config)
            if len(sig.parameters)
            else design_coro()
        )
        asyncio.run(run_coro)

    design_config["module"] = design_mod
    return design_config
