# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional
import sys
from pathlib import Path
from importlib import import_module

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import toml

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.defaults import DEFAULT_NETCAD_CONFIG_FILE

from netcad.config import globals

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def load(config_filepath: Optional[Path] = None):

    if not config_filepath:
        config_filepath = Path(DEFAULT_NETCAD_CONFIG_FILE)

    if not config_filepath.is_file():
        raise FileNotFoundError(str(config_filepath.absolute()))

    globals.g_netcad_config = toml.load(config_filepath.open())
    return globals.g_netcad_config


def import_networks(root_path):
    sys.path.insert(0, root_path)
    pkg_list = globals.g_netcad_config["networks"]
    for pkg in pkg_list:
        import_module(pkg)
