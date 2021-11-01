# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional
from importlib import import_module
from functools import lru_cache
import json

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import aiofiles

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import netcad_globals
from netcad.registry import Registry

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["Origin"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class Origin(Registry, registry_name="origins"):
    package: Optional[str] = None
    origin_name: Optional[str] = None

    # -------------------------------------------------------------------------
    #
    #                               Class Methods
    #
    # -------------------------------------------------------------------------

    @classmethod
    def import_origin(cls, package: str):
        """
        import_origin is used to import a given origin python module using the
        standard dot-colon nation.

        Parameters
        ----------
        package: str
            The package name is dot-colon format.

        Returns
        -------
        The class representing the origin so that the Caller can use the class for
        class specific functions/instance creation.
        """
        module, _, name = package.rpartition(":")
        try:
            import_module(module)

        except ModuleNotFoundError:
            raise RuntimeError(f"Unable to import origin module: {module}")

        if not (origin_cls := cls.registry_get(name)):
            raise RuntimeError(
                f"Missing expected class: {name} for origin module: {module}"
            )

        return origin_cls

    @classmethod
    @lru_cache
    def cache_load(cls, cache_subdir: str, cache_item_name: str):
        dt_dir = netcad_globals.g_netcad_cache_dir.joinpath(cache_subdir)
        payload_file = dt_dir.joinpath(f"{cache_item_name}.json")
        payload = json.load(payload_file.open())

        # get the origin name -> package translation from the configuration
        # files

        try:
            origin_name = payload["netcad.origin"]
            origin_obj = netcad_globals.g_config["origin"][origin_name]
            origin_package = origin_obj["package"]

        except KeyError:
            raise RuntimeError(
                f'Missing expected "netcad.origin" key in device-type file: {payload_file}'
            )

        # import the origin package file, returning the class associated with
        # this specific origin type

        origin_cls = cls.import_origin(origin_package)
        return origin_cls(payload)

    async def cache_save(self, cache_subdir: str, cache_item_name: str, payload: dict):
        cache_dir = netcad_globals.g_netcad_cache_dir
        dt_dir = cache_dir.joinpath(cache_subdir)
        pm_file = dt_dir.joinpath(f"{cache_item_name}.json")
        payload["netcad.origin"] = self.origin_name

        async with aiofiles.open(str(pm_file.absolute()), "w+") as ofile:
            await ofile.write(json.dumps(payload, indent=3))

    # -------------------------------------------------------------------------
    #
    #                   Registry __dunder__ Overrides
    #
    # -------------------------------------------------------------------------

    def __init_subclass__(cls, **kwargs):
        """
        Automatically registger subclasses of Origin by the `origin_name`
        attribute value. This mechanism allows for the specific instances of
        Origin, NetboxOrigin, for example, to be registgered by their name for
        import/usage purposes.
        """
        if not cls.origin_name:
            super().__init_subclass__(**kwargs)
            return

        cls.registry_add(name=cls.origin_name, obj=cls)
