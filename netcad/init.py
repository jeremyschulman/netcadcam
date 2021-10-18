# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from os import environ
from pathlib import Path

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import toml

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import netcad_globals
from netcad.config.envvars import Environment
from netcad.defaults import DEFAULT_NETCAD_CONFIG_FILE

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["init"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def init():
    """
    The netcad primary initialization function.
    """

    # The NETCAD_CONFIGFILE designates the location of the netcad configuration
    # file. by default this is "netcad.toml" in the $CWD.

    config_filepath = environ.setdefault(
        Environment.NETCAD_CONFIGFILE, DEFAULT_NETCAD_CONFIG_FILE
    )
    config_filepath = Path(config_filepath).absolute()
    environ[Environment.NETCAD_CONFIGFILE] = str(config_filepath)

    netcad_globals.g_config = toml.load(config_filepath.open())

    # The NETCAD_PROJECTDIR, by default is the parent of the config-file.

    project_dir = Path(
        environ.setdefault(
            Environment.NETCAD_PROJECTDIR, str(config_filepath.parent.absolute())
        )
    )

    netcad_globals.g_netcad_project_dir = project_dir

    # The NETCAD_CACHDIR, by default is ".netcad" located in the NETCAD_PROJDIR.

    environ.setdefault(
        Environment.NETCAD_CACHEDIR, str(project_dir.joinpath(".netcad").absolute())
    )
