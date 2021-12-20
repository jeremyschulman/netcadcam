# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import os
from typing import Dict, List, Optional
from types import ModuleType

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import netcad_globals, loader

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["import_netcam_plugins", "NetcamPluginCatalog"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

NetcamPluginCatalog = Dict[str, "NetcamPlugin"]


class NetcamPlugin:

    REQUIREMENTS = ["plugin_version", "plugin_init", "plugin_get_dut"]

    OPTIONALS = ["plugin_description"]

    def __init__(self, config: dict):
        self.config = config
        self.name = config["name"]
        self.description = config.get("description")

        self.supports: Optional[List[str]] = None
        self.package: Optional[str] = None
        self.module: Optional[ModuleType] = None

        self._export_env()
        self._validate_config()

    def _export_env(self):
        # if the section contains an "env" dictinary, then use those values to
        # export the User provided values.

        if not (pg_cfg_env := self.config.get("env")):
            return

        for var_name, var_val in pg_cfg_env.items():
            os.environ[var_name] = var_val

    def _validate_config(self):
        self.package = self.config.get("package")
        if not self.package:
            raise RuntimeError(f'Plugin {self.name}: missing "package"')

        self.supports = self.config.get("supports")
        if not self.supports:
            raise RuntimeError(
                f'Plugin {self.name}: missing "supports" list of os-names'
            )

    def import_plugin(self):
        try:
            self.module = loader.import_objectref(self.package)

        except ModuleNotFoundError:
            raise RuntimeError(
                f"Plugin {self.name} package {self.package} not found in Python environment"
            )
        except ImportError as exc:
            rt_exc = RuntimeError(
                f"Plugin {self.name} package {self.package}: failed to import",
            )
            rt_exc.__traceback__ = exc.__traceback__
            raise rt_exc

        self._validate_module()

    def _validate_module(self):
        pkg_ref = f"Plugin {self.name} package {self.package}"

        for mod_attr_name in self.REQUIREMENTS:
            if not (attr_val := getattr(self.module, mod_attr_name, None)):
                raise RuntimeError(f"{pkg_ref}: missing required {mod_attr_name}")

            setattr(self, mod_attr_name, attr_val)

        for mod_attr_name in self.OPTIONALS:
            attr_val = getattr(self.module, mod_attr_name, None)
            setattr(self, mod_attr_name, attr_val)


def import_netcam_plugins() -> NetcamPluginCatalog:
    """
    This function imports the Python module defined in the User configuration
    file "netcam.package", and returns that module so that the Caller can use
    the `get_dut` function.

    Returns
    -------
    The plugin module as described.
    """

    cfg_file = netcad_globals.g_netcad_config_file.absolute()

    try:
        plugins_cfglist = netcad_globals.g_config["netcam"]["plugins"]

    except KeyError:
        raise RuntimeError(f'Configuration "netcam.plugins" missing: {cfg_file}')

    netcad_globals.g_netcam_plugins = list()
    netcad_globals.g_netcam_plugins_catalog = dict()

    for pg_id, pg_item in enumerate(plugins_cfglist, start=1):

        pg_obj = NetcamPlugin(config=pg_item)
        pg_obj.import_plugin()

        netcad_globals.g_netcam_plugins.append(pg_obj)

        for os_name in pg_obj.supports:
            netcad_globals.g_netcam_plugins_catalog[os_name] = pg_item

    return netcad_globals.g_netcam_plugins_catalog
