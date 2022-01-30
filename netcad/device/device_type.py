#  Copyright (c) 2021-2022 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Iterable, AnyStr

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic.dataclasses import dataclass

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.cache import Cache


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["DeviceType", "DeviceTypeInterfaceSpec"]


@dataclass()
class DeviceTypeInterfaceSpec:
    if_name: str
    if_type: str
    if_type_label: str


class DeviceType:
    CACHE_SUBDIR = "device-types"

    def __init__(self, origin_spec):
        self.origin_spec = origin_spec

    @property
    def device_type(self) -> str:
        raise NotImplementedError()

    @property
    def interface_names(self) -> Iterable[AnyStr]:
        raise NotImplementedError()

    def get_interface(self, if_name: str) -> DeviceTypeInterfaceSpec:
        raise NotImplementedError()

    @classmethod
    def load(cls, name: str) -> "DeviceType":
        spec = Cache(subdir=cls.CACHE_SUBDIR).cache_load(cache_item_name=name)
        return spec.factory("DeviceType")
