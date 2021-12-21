from netcad.config import netcad_globals
from netcad.plugins import NetcadPlugin


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
        pg_obj.init()

        netcad_globals.g_netcad_plugins.append(pg_obj)
        netcad_globals.g_netcad_plugins_catalog[pg_obj.name] = pg_obj

    return netcad_globals.g_netcam_plugins_catalog
