#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import netcad_globals
from netcad.plugins import NetcadPlugin

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["init_netcad_user_plugins"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def init_netcad_user_plugins():

    # if there are no User defined plugins, then return.
    try:
        plugins_cfglist = netcad_globals.g_config["netcad"]["plugins"]

    except KeyError:
        # TODO: log this with a debug messagte
        return

    netcad_globals.g_netcad_plugins = list()
    netcad_globals.g_netcad_plugins_catalog = dict()

    for pg_id, pg_item in enumerate(plugins_cfglist, start=1):

        pg_obj = NetcadPlugin(config=pg_item)
        pg_obj.load()

        netcad_globals.g_netcad_plugins.append(pg_obj)
        netcad_globals.g_netcad_plugins_catalog[pg_obj.name] = pg_obj

    return netcad_globals.g_netcad_plugins_catalog
