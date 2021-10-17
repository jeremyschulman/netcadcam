# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, AnyStr
import sys
import os
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

from netcad.config import netcad_globals

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def load(config_filepath: Optional[AnyStr] = None):

    config_filepath = Path(config_filepath or DEFAULT_NETCAD_CONFIG_FILE)
    if not config_filepath.is_file():
        raise FileNotFoundError(str(config_filepath.absolute()))

    netcad_globals.g_config_file = config_filepath
    netcad_globals.g_config = toml.load(config_filepath.open())

    project_dir = os.environ.setdefault(
        "NETCAD_PROJECTDIR", str(config_filepath.parent.absolute())
    )

    project_dir = Path(project_dir)
    netcad_globals.g_netcad_project_dir = project_dir

    return netcad_globals.g_config


def import_networks(root_path: Path):
    sys.path.insert(0, str(root_path))
    pkg_list = netcad_globals.g_config["networks"]
    for pkg in pkg_list:
        import_module(pkg)
