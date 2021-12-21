from typing import Optional, List, Callable
from types import ModuleType

from netcad.config import loader


class NetcadPlugin:

    REQUIREMENTS = ["plugin_version", "plugin_init"]
    OPTIONALS = ["plugin_description", "plugin_author"]

    def __init__(self, config: dict):
        self.config = config
        self.name: Optional[str] = None
        self.package: Optional[str] = None
        self.description = config.get("description")

        self._validate_config()

        self.supports: Optional[List[str]] = None
        self.module: Optional[ModuleType] = None
        self.plugin_init: Optional[Callable] = None

    def _validate_config(self):

        if not (plugin_name := self.config.get("name")):
            raise RuntimeError(
                f'Error netcad.plugins: config exists without a "name" value, please correct: {self.config=}'
            )
        self.name = plugin_name

        self.package = self.config.get("package")
        if not self.package:
            raise RuntimeError(f'Plugin {self.name}: missing "package"')

    def init(self):
        self.import_plugin()
        self.plugin_init(self.config)

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
