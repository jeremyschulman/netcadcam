#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import types
from typing import Optional, Protocol, get_args, get_type_hints, Dict
from typing import TYPE_CHECKING
import inspect

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.init.loader import netcad_import_package

if TYPE_CHECKING:
    from netcad.netcam.dut import DeviceUnderTest

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "NetcadPluginModule",
    "NetcamPluginModule",
    "NetcamPlugin",
    "NetcadPlugin",
    "PluginCatalog",
]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class NetcadPluginModule(Protocol):
    plugin_version: str
    plugin_description: Optional[str] = None
    plugin_author: Optional[str] = None

    def plugin_init(self, config: dict):
        """The plugin initialization function"""


class NetcamPluginModule(NetcadPluginModule):
    def plugin_get_dut(self, device: "Device") -> "DeviceUnderTest":
        """Obtain the DUT instance for a given Device instance"""


class Plugin:
    _plugin_typeref = NetcadPluginModule

    def __init__(self, config: dict):
        self.config = config
        self.name: Optional[str] = None
        self.package: Optional[str] = None
        self.description = config.get("description")

        self.module: Optional[Plugin._plugin_typeref] = None
        self._plugin_requires = set()
        self._plugin_optionals = set()

        self._validate_config()
        self._introspect_pluginref()

    def _introspect_pluginref(self):
        def predicate(v):
            return inspect.isfunction(v) and v.__name__.startswith("plugin_")

        none_type = type(None)

        for attr, hint in get_type_hints(self.__class__._plugin_typeref).items():
            hint_args = get_args(hint)
            if none_type in hint_args:
                self._plugin_optionals.add(attr)
            else:
                self._plugin_requires.add(attr)

        pl_methods = [
            name
            for name, obj in inspect.getmembers(
                self.__class__._plugin_typeref, predicate=predicate
            )
        ]

        self._plugin_requires.update(pl_methods)

    def load(self):
        self.import_plugin()
        self.module.plugin_init(self.config.get("config"))

    def _validate_config(self):
        self.name = self.config.get("name")
        if not self.name:
            raise RuntimeError(
                f'Error netcad.plugins: config exists without a "name" value, please correct: {self.config=}'
            )

        self.package = self.config.get("package")
        if not self.package:
            raise RuntimeError(f'Plugin {self.name}: missing "package"')

    def import_plugin(self):
        def _plugin_silent(_self, _item: str):
            if _item.startswith("plugin_"):
                return None
            raise AttributeError(_item)

        try:
            self.module = netcad_import_package(self.package)
            self.module.__getattr__ = types.MethodType(_plugin_silent, self.module)

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

        for mod_attr_name in self._plugin_requires:
            if not getattr(self.module, mod_attr_name, None):
                raise RuntimeError(f"{pkg_ref}: missing required {mod_attr_name}")

    def __getattr__(self, item):
        if item.startswith("plugin_"):
            return getattr(self.module, item)

        raise AttributeError(item)


class NetcadPlugin(Plugin):
    _plugin_typeref = NetcadPluginModule


class NetcamPlugin(Plugin):
    _plugin_typeref = NetcamPluginModule


PluginCatalog = Dict[str, Plugin]
