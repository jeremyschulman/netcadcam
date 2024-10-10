#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from pathlib import Path

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import click

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import netcad_globals
from netcad.config import Environment

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

opt_devices = lambda **params: click.option(  # noqa
    "-d",
    "--device",
    "devices",
    metavar="[DEVICE-NAME]",
    help="device hostname(s)",
    multiple=True,
    **params,
)


def unique_required_design_collection(ctx, param, value):
    # if the User provided values, then use these before any exported into the
    # enviornment.

    from_env = netcad_globals.g_userenv_design_names

    if not value and not from_env:
        raise click.exceptions.MissingParameter(
            message="design required, not found in enviornment or CLI",
            ctx=ctx,
            param=param,
        )

    # given the design name either provided by the CLI or in the User
    # enviornment, ensure that each of these design names are actually present
    # in the design configuration file.

    given_designs = list(dict.fromkeys(value)) if value else from_env

    missing = {
        name for name in given_designs if name not in netcad_globals.g_netcad_designs
    }
    if missing:
        mlist = ", ".join(missing)
        raise click.exceptions.BadParameter(
            message=f'Given design names are not found in configuration file: "{mlist}"',
            ctx=ctx,
            param=param,
        )

    return given_designs


opt_designs = lambda **params: click.option(  # noqa
    "-D",
    "--design",
    "designs",
    multiple=True,
    metavar="[DESIGN]",
    help="design(s)",
    callback=unique_required_design_collection,
    **params,
)

opt_design = lambda **params: click.option(  # noqa
    "-D", "--design", "design", metavar="[DESIGN]", help="design", **params
)


opt_design_features = lambda **params: click.option(  # noqa
    "--feature",
    "features",
    multiple=True,
    help="execute only these design checks",
)

opt_configs_dir = lambda **params: click.option(
    "--configs-dir",
    "configs_dir",
    help="location to store configs",
    type=click.Path(path_type=Path, resolve_path=True, exists=True, writable=True),
    envvar=Environment.NETCAD_CONFIGSDIR,
    default="configs",
)
