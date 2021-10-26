# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Iterable, AnyStr, Optional
from functools import lru_cache
import json

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import aiofiles
from pydantic.dataclasses import dataclass

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import netcad_globals


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["OriginDeviceType", "OriginDeviceTypeInterfaceSpec"]


@dataclass()
class OriginDeviceTypeInterfaceSpec:
    if_name: str
    if_type: str
    if_type_label: str


class OriginDeviceType(object):
    package: Optional[str] = None

    def __init__(self, origin_name, origin_spec):
        self.origin_name = origin_name
        self.origin_spec = origin_spec

    @property
    def product_model(self) -> str:
        raise NotImplementedError()

    @property
    def interface_names(self) -> Iterable[AnyStr]:
        raise NotImplementedError()

    def get_interface(self, if_name: str) -> OriginDeviceTypeInterfaceSpec:
        raise NotImplementedError()

    @staticmethod
    @lru_cache
    def cache_load(product_model: str) -> "OriginDeviceType":
        from netcad.origin import Origin

        dt_dir = netcad_globals.g_netcad_cache_dir.joinpath("device-types")
        pm_file = dt_dir.joinpath(f"{product_model}.json")
        payload = json.load(pm_file.open())

        try:
            origin = payload["netcad.origin"]
        except KeyError:
            raise RuntimeError(
                f'Missing expected "netcad.origin" key in device-type file: {pm_file}'
            )

        origin_cls = Origin.import_origin(origin)
        return origin_cls.device_type(
            origin_name=origin_cls.register_name, origin_spec=payload
        )

        # cache_dir = netcad_globals.g_netcad_cache_dir
        # dt_dir = cache_dir.joinpath("device-types")
        # pm_file = dt_dir.joinpath(f"{product_model}.json")
        # payload = json.load(pm_file.open())
        # origin_name = payload["netcad.origin"]

    async def cache_save(self):
        cache_dir = netcad_globals.g_netcad_cache_dir
        dt_dir = cache_dir.joinpath("device-types")
        pm_file = dt_dir.joinpath(f"{self.product_model}.json")
        self.origin_spec["netcad.origin"] = f"{self.package}:{self.origin_name}"

        async with aiofiles.open(str(pm_file.absolute()), "w+") as ofile:
            await ofile.write(json.dumps(self.origin_spec, indent=3))

    @classmethod
    async def get(cls, origin_cls, product_models: Iterable[AnyStr]):
        """
        Gets the collection of product models from the origin and saves them to
        the cache filesystem.

        Parameters
        ----------
        origin_cls: Origin

        product_models:
            List of product-model string values.

        """
        raise NotImplementedError()
