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
from netcad.test_services import init_import_testing_services

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["init"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def ensure_directory(project_dir: Path, env_var: str, default_value: str):

    dir_path = Path(
        environ.setdefault(
            env_var,
            str(project_dir.joinpath(default_value).absolute()),
        )
    )

    dir_path.mkdir(exist_ok=True)
    return dir_path


def init():
    """
    The netcad primary initialization function.
    """

    # -------------------------------------------------------------------------
    # NETCAD_CONFIGFILE, designates the location of the netcad configuration
    # file. by default this is "netcad.toml" in the $CWD.
    # -------------------------------------------------------------------------

    config_filepath = environ.setdefault(
        Environment.NETCAD_CONFIGFILE, d.DEFAULT_NETCAD_CONFIG_FILE
    )
    config_filepath = netcad_globals.g_netcad_config_file = Path(
        config_filepath
    ).absolute()
    environ[Environment.NETCAD_CONFIGFILE] = str(config_filepath)

    netcad_globals.g_config = toml.load(config_filepath.open())

    # -------------------------------------------------------------------------
    # NETCAD_PROJECTDIR, by default is the parent of the config-file.
    # -------------------------------------------------------------------------

    project_dir = netcad_globals.g_netcad_project_dir = Path(
        environ.setdefault(
            Environment.NETCAD_PROJECTDIR, str(config_filepath.parent.absolute())
        )
    )

    # -------------------------------------------------------------------------
    # NETCAD_CONFIGSSDIR
    # -------------------------------------------------------------------------

    netcad_globals.g_netcad_configsdir_dir = ensure_directory(
        project_dir,
        env_var=Environment.NETCAD_CONFIGSDIR,
        default_value=d.DEFAULT_NETCAD_CONFIGSDIR,
    )

    # -------------------------------------------------------------------------
    # NETCAD_TESTCASESDIR
    # -------------------------------------------------------------------------

    netcad_globals.g_netcad_testcases_dir = ensure_directory(
        project_dir=project_dir,
        env_var=Environment.NETCAD_TESTCASESDIR,
        default_value=d.DEFAULT_NETCAD_TESTCASESDIR,
    )

    # -------------------------------------------------------------------------
    # NETCAD_CACHDIR
    # -------------------------------------------------------------------------

    netcad_globals.g_netcad_cache_dir = Path(
        environ.setdefault(
            Environment.NETCAD_CACHEDIR,
            str(project_dir.joinpath(d.DEFAULT_NETCAD_CACHEDIR).absolute()),
        )
    )

    # import the testing services modules so that they are retrievable via the
    # Registry mechanism.

    init_import_testing_services.on_init()
