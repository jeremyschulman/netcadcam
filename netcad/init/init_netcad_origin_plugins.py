#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import netcad_globals
from netcad.plugins import NetcadOriginPlugin, NetcadOriginPluginCatalog

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["init_netcad_origin_plugins", "NetcadOriginPluginCatalog"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def init_netcad_origin_plugins() -> Optional[NetcadOriginPluginCatalog]:

    # if there are no User defined plugins, then return.
    try:
        origins_list = netcad_globals.g_config["netcad"]["origin"]

    except KeyError:
        # TODO: log this with a debug messagte
        return

    netcad_globals.g_netcad_plugins_catalog = NetcadOriginPlugin.init(origins_list)

    return netcad_globals.g_netcad_plugins_catalog
