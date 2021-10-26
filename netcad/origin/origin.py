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
    name = None
    device_type: Optional[Type[OriginDeviceType]] = None

    def __init_subclass__(cls, **kwargs):
        cls.registry_add(cls.name, cls)

    @classmethod
    def import_origin(cls, name) -> "Origin":
        try:
            import_module(name=name)
        except ModuleNotFoundError:
            raise RuntimeError(f"Unable to import device-types origin module: {name}")

        return Origin.registry_get(name)
