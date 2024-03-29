#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

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

from netcad.config import netcad_globals, defaults as d
from netcad.config import Environment
from netcad.config.loader import import_objectref
from .init_device_types import init_import_device_types

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
    The netcad / netcam primary initialization function.
    """

    _init_debug()
    _init_config_contents()
    _init_proj_dirs()
    init_import_device_types(netcad_globals.g_config)
    _init_design_configs()
    _init_user_environment()


# -----------------------------------------------------------------------------
#
#                               PRIVATE CODE BEGINS
#
# -----------------------------------------------------------------------------


def _init_debug():
    errmsg = None

    if not (debug_val := environ.get("NETCAD_DEBUG")):
        return

    if not (debug_val.isdigit()):
        errmsg = f"NETCAD_DEBUG value must be >= 0: {debug_val}, debug is disabled."
        debug_val = 1

    netcad_globals.g_debug_level = int(debug_val)

    from netcad.logger import get_logger

    log = get_logger()

    if errmsg:
        log.error(f"NETCAD_DEBUG '{debug_val}' set to {netcad_globals.g_debug_level}")
    else:
        log.debug(f"NETCAD_DEBUG set to {netcad_globals.g_debug_level}")


def _init_design_configs():
    # Add the project directory to the Python system path so that packages can
    # be imported without the User installing them.

    sys.path.insert(0, environ[Environment.NETCAD_PROJECTDIR])

    # If the User exports a set of design-names they want to use by default so
    # they do not need to provide that flag on each invocation, then setup that
    # global variable now.
    #
    # Note: the following code uses a technique to get the ordered list of
    #       unique values.  Reference:
    #       https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-whilst-preserving-order

    if userenv_design := environ.get(Environment.NETCAD_DESIGN):
        netcad_globals.g_userenv_design_names = list(
            dict.fromkeys(userenv_design.split(":"))
        )

    # Ensure the User actually defined some 'design' items in their configuration file.

    if not (design_configs := netcad_globals.g_config.get("design")):
        raise RuntimeError(
            f'Missing "design" definitions in config file: "{netcad_globals.g_netcad_config_file}"'
        )

    # Initialize the g_netcad_designs global to the contents of the config file
    # so that this can be easily referenced later when loading designs.

    netcad_globals.g_netcad_designs = {
        design_cfg["name"]: design_cfg for design_cfg in design_configs
    }


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

    netcad_globals.g_netcad_checks_dir = ensure_directory(
        project_dir=project_dir,
        env_var=Environment.NETCAD_CHECKSDIR,
        default_value=d.DEFAULT_NETCAD_CHECKSDIR,
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

    from netcad.logger import get_logger

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
