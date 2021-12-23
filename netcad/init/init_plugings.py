from typing import Optional

from netcad.config import netcad_globals
from netcad.plugins import NetcadPlugin, NetcamPlugin, PluginCatalog


def init_netcad_plugins():

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


def import_netcam_plugins() -> Optional[PluginCatalog]:
    """
    Load the netcam.plugins as defined in the User configuration file.

    The netcam globals, g_netcam_plugins and g_netcam_plugins_catalog, will be
    initialized.  The catalog will be key'd by the os_name values defined in the
    User configuration file for the specific plugin.
    """

    # if there are no User defined plugins, then return.
    try:
        plugins_cfglist = netcad_globals.g_config["netcam"]["plugins"]

    except KeyError:
        # TODO: log this with a debug messagte
        return

    netcad_globals.g_netcam_plugins = list()
    netcad_globals.g_netcam_plugins_os_catalog = dict()

    for pg_id, pg_item in enumerate(plugins_cfglist, start=1):

        pg_obj = NetcamPlugin(config=pg_item)
        pg_obj.load()

        netcad_globals.g_netcam_plugins.append(pg_obj)
        for os_name in pg_obj.config["supports"]:
            netcad_globals.g_netcam_plugins_os_catalog[os_name] = pg_obj

    return netcad_globals.g_netcam_plugins_os_catalog
