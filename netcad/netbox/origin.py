# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import AnyStr, Iterable

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from httpx import Response

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.igather import as_completed
from netcad.logger import get_logger
from netcad.origin import Origin
from .devices import NetboxDevices

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["OriginNetbox"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class OriginNetbox(Origin):
    async def get_device_types(self, product_models: Iterable[AnyStr]):
        """
        This function is used to fetch the specified device-types given the list
        of provided `product_models`.  Each of these device-type definitons will
        be stored in the Userss cache-directory as:

        $NETCAD_CACHEDIR/device-types/<porduct-modulel>.json

        Parameters
        ----------
        product_models:
            expected Sequences of strings used for the purpose of fetching the
            device-type definitions from the origin.

        Returns
        -------

        """
        log = get_logger()
        dt_dir = self.cache_dir.joinpath("device-types")
        dt_dir.mkdir(exist_ok=True)

        nb: NetboxDevices

        async with NetboxDevices() as nb:
            tasks = {
                nb.fetch_device_template(model=model): model for model in product_models
            }

            task_results: Response

            async for orig_coro, model_payload in as_completed(tasks):
                model = tasks[orig_coro]
                if not model_payload:
                    log.error(f"Execpted device-type {model} not found in Netbox")
                    continue

                log.info(f"Saving device-type: {model}")
                await self.save_file(dt_dir.joinpath(f"{model}.json"), model_payload)
