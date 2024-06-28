#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Optional

from netcad.config import netcad_globals
from netcad.plugins import NetcamPlugin, PluginCatalog
from .loader import netcad_import_package


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

        if not (supported_os := pg_obj.config.get("supports")):
            raise RuntimeError(
                f"netcam plugin {pg_obj.name} missing 'supports' OS name list definition"
            )

        for os_name in supported_os:
            netcad_globals.g_netcam_plugins_os_catalog[os_name] = pg_obj

        if not (svcs := pg_obj.config.get("features")):
            raise RuntimeError(
                f"netcam plugin {pg_obj.name} missing 'features' package list definition"
            )

        for svc_pkg in svcs:
            try:
                netcad_import_package(svc_pkg)
            except ImportError as exc:
                raise RuntimeError(
                    f"Unable to import DUT {pg_obj.name} module {svc_pkg}: {str(exc)}"
                )

    return netcad_globals.g_netcam_plugins_os_catalog
