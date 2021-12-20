# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------
import asyncio
import sys
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
from netcad.config.loader import import_objectref
from netcad.logger import get_logger

from netcad import defaults as d

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
    The netcad/cam primary initialization function.
    """

    _init_debug()
    _init_config_contents()
    _init_proj_dirs()
    _init_design_configs()
    _init_user_environment()


# -----------------------------------------------------------------------------
#
#                               PRIVATE CODE BEGINS
#
# -----------------------------------------------------------------------------


def _init_debug():

    log = get_logger()

    if not (debug_val := environ.get("NETCAD_DEBUG")):
        return

    if not (debug_val.isdigit()):
        log.error(f"NETCAD_DEBUG value must be >= 0: {debug_val}, debug is disabled.")

    netcad_globals.g_debug_level = int(debug_val)
    log.debug(f"NETCAD_DEBUG set to {netcad_globals.g_debug_level}")


def _init_design_configs():
    # Add the project directory to the Python system path so that packages can
    # be imported without the User installing them.

    sys.path.insert(0, environ[Environment.NETCAD_PROJECTDIR])

    if not (design_configs := netcad_globals.g_config.get("design")):
        raise RuntimeError(
            f'Missing "design" definitions in config-file: {netcad_globals.g_netcad_config_file}'
        )

    # Initialize the g_netcad_designs global to the contents of the config file
    # so that this can be easily referenced later when loading designs.

    netcad_globals.g_netcad_designs = design_configs


def _init_config_contents():

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

    if not config_filepath.is_file():
        raise RuntimeError(
            f"Netcad configuration file not found: {config_filepath.absolute()}"
        )
    netcad_globals.g_config = toml.load(config_filepath.open())


def _init_proj_dirs():

    # -------------------------------------------------------------------------
    # NETCAD_PROJECTDIR, by default is the parent of the config-file.
    # -------------------------------------------------------------------------

    project_dir = netcad_globals.g_netcad_project_dir = Path(
        environ.setdefault(
            Environment.NETCAD_PROJECTDIR,
            str(netcad_globals.g_netcad_config_file.parent.absolute()),
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
    # NETCAD_TEMPLATESDIR
    # -------------------------------------------------------------------------

    netcad_globals.g_netcad_templates_dir = ensure_directory(
        project_dir=project_dir,
        env_var=Environment.NETCAD_TEMPLATESDIR,
        default_value=d.DEFAULT_NETCAD_TEMPLATESDIR,
    )

    # -------------------------------------------------------------------------
    # NETCAD_CACHDIR
    # -------------------------------------------------------------------------

    netcad_globals.g_netcad_cache_dir = ensure_directory(
        project_dir=project_dir,
        env_var=Environment.NETCAD_CACHEDIR,
        default_value=d.DEFAULT_NETCAD_CACHEDIR,
    )


def _init_user_environment():

    # if the User did not provision an entry point reference then nothing more
    # to do here; just log a debug for safekeeping.

    log = get_logger()

    try:
        env_entry_point_ref = netcad_globals.g_config["environment"]["entry_point"]
    except KeyError:
        log.debug("No user-defined environment entry-point in configuration file.")
        return

    ep_obj = import_objectref(object_ref=env_entry_point_ref)

    if asyncio.iscoroutine(ep_obj):
        asyncio.run(ep_obj())
    elif callable(ep_obj):
        ep_obj()
    else:
        log.error(
            f"User environment entry-point {env_entry_point_ref} is not callable."
        )


def ensure_directory(project_dir: Path, env_var: str, default_value: str):

    dir_path = Path(
        environ.setdefault(
            env_var,
            str(project_dir.joinpath(default_value).absolute()),
        )
    )

    dir_path.mkdir(exist_ok=True)
    return dir_path
