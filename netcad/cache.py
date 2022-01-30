#  Copyright (c) 2021-2022 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import json
from functools import lru_cache

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import aiofiles

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import netcad_globals

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["Cache"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class CacheItem:
    def __init__(self, origin, payload):
        self.origin = origin
        self.payload = payload

    def factory(self, cls_name: str):
        if not (maker := getattr(self.origin.module, "plugin_origin_item")):
            raise RuntimeError(
                f'Origin "{self.origin.name}" missing plugin_origin_item function, check code'
            )
        return maker(cls_name, self.payload)


class Cache:
    def __init__(self, subdir: str):
        self.cache_subdir = netcad_globals.g_netcad_cache_dir / subdir
        self.cache_subdir.mkdir(exist_ok=True)

    @lru_cache
    def cache_load(self, cache_item_name: str):

        payload_file = self.cache_subdir / f"{cache_item_name}.json"
        payload = json.load(payload_file.open())

        if not (origin_name := payload.get("netcad.origin")):
            raise RuntimeError(
                f'Missing expected "netcad.origin" key in device-type file: {payload_file}'
            )

        if not (
            origin_obj := netcad_globals.g_netcad_origin_plugins_catalog.get(
                origin_name
            )
        ):
            raise RuntimeError(
                f'Missing origin plugin "{origin_name}", check config-file'
            )

        return CacheItem(origin=origin_obj, payload=payload)

    async def cache_save(
        self,
        cache_item_name: str,
        payload: dict,
        origin_name: str,
    ):
        pm_file = self.cache_subdir / f"{cache_item_name}.json"
        payload["netcad.origin"] = origin_name

        async with aiofiles.open(str(pm_file.absolute()), "w+") as ofile:
            await ofile.write(json.dumps(payload, indent=3))
