#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from httpx import Response

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.design import Design
from netcad.cache import Cache
from netcad.igather import as_completed

# -----------------------------------------------------------------------------
# Private Module Imports
# -----------------------------------------------------------------------------

from ..devices import NetboxDevices

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["plugin_origin_pull"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


async def plugin_origin_pull(design: Design, **options):
    services = options.get("services")

    if "device-types" in services:
        await pull_device_types(design)


# -----------------------------------------------------------------------------
#
#                              PRIVATE CODE BEGINS
#
# -----------------------------------------------------------------------------


async def pull_device_types(design: Design):

    log = get_logger()
    errors = 0
    device_types = set()

    cache = Cache(subdir="device-types")

    for device in design.devices.values():
        if not (pull_value := device.device_type or device.product_model):
            log.error(
                f"Device '{device.name}': missing device_type and product_model assignement"
            )
            errors += 1
            continue
        device_types.add(pull_value)

    log.info(f"PULL: netbox.device-types: {device_types}")

    async with NetboxDevices() as nb:
        tasks = {nb.fetch_device_template(model=model): model for model in device_types}

        task_results: Response
        async for orig_coro, model_payload in as_completed(tasks):
            model = tasks[orig_coro]

            if not model_payload:
                log.error(f"Execpted device-type {model} not found in Netbox")
                continue

            await cache.cache_save(
                origin_name="netbox", cache_item_name=model, payload=model_payload
            )
            log.debug(f"SAVE: netbox.device-types: {model}")
