# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Type
from importlib import import_module

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.registry import Registry
from .origin_device_type import OriginDeviceType


class Origin(Registry):
    register_name = "origin"
    device_type: Optional[Type[OriginDeviceType]] = None

    @classmethod
    def import_origin(cls, package: str) -> "Origin":
        module, _, name = package.rpartition(":")

        try:
            import_module(module)

        except ModuleNotFoundError:
            raise RuntimeError(f"Unable to import device-types origin module: {name}")

        return Origin.registry_get(name)
