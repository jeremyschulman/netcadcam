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
from netcad.config import Environment
from netcad import defaults as d
from netcad.testing import init_import_testing_services

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
        Environment.NETCAD_CONFIGFILE, d.DEFAULT_NETCAD_CONFIG_FILE
    )
    config_filepath = Path(config_filepath).absolute()
    environ[Environment.NETCAD_CONFIGFILE] = str(config_filepath)

    netcad_globals.g_config = toml.load(config_filepath.open())

    # NETCAD_PROJECTDIR, by default is the parent of the config-file.

    project_dir = netcad_globals.g_netcad_project_dir = Path(
        environ.setdefault(
            Environment.NETCAD_PROJECTDIR, str(config_filepath.parent.absolute())
        )
    )

    # NETCAD_TESTCASESDIR

    netcad_globals.g_netcad_testcases_dir = Path(
        environ.setdefault(
            Environment.NETCAD_TESTCASESDIR,
            str(project_dir.joinpath(d.DEFAULT_NETCAD_TESTCASESDIR).absolute()),
        )
    )

    # NETCAD_CACHDIR

    netcad_globals.g_netcad_cache_dir = Path(
        environ.setdefault(
            Environment.NETCAD_CACHEDIR,
            str(project_dir.joinpath(d.DEFAULT_NETCAD_CACHEDIR).absolute()),
        )
    )

    init_import_testing_services.on_init()
