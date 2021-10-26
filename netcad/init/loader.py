# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, AnyStr, List
from types import ModuleType
import sys
import os
from importlib import import_module

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------


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


def import_networks(root_path: Optional[AnyStr] = None) -> List[ModuleType]:

    # Add the User's project directory for python import path.

    sys.path.insert(0, root_path or os.environ[Environment.NETCAD_PROJECTDIR])

    # the config file should have a networks section that defines the list of
    # python modules to import.

    if not (pkg_list := netcad_globals.g_config.get("networks")):
        raise RuntimeError(
            f'Missing "networks" definition in config-file: {netcad_globals.g_netcad_config_file}'
        )

    try:
        return [import_module(pkg) for pkg in pkg_list]

    except ImportError as exc:
        raise RuntimeError(f"Unable to load network module: {exc.args[0]}")
