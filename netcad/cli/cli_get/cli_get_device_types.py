import asyncio
from typing import AnyStr, Iterable
from importlib import import_module

from netcad.origin import Origin
from netcad.logger import get_logger
from netcad.cli.main import clig_get
from netcad.config import netcad_globals
from netcad.device import Device


async def get_device_types(origin: Origin, product_models: Iterable[AnyStr]):
    await origin.get_device_types(product_models)


@clig_get.command(name="device-types")
def clig_get_device_types():
    log = get_logger()

    config = netcad_globals.g_config
    try:
        origin = config["get"]["device-types"]
        origin_module = import_module(name=origin)

    except ModuleNotFoundError as exc:
        raise RuntimeError(
            f'Unable to import origin module: {exc.args[0]}'
        )

    except KeyError as exc:
        raise RuntimeError(
            "Unable to find [get.device-types] in configuration file: "
            f"{netcad_globals.g_netcad_config_file.absolute()}"
        )

    if not (origin_cls := getattr(origin_module, 'Origin', None)):
        raise RuntimeError(
            f'Origin module: {origin} does not define Origin class.'
        )

    # find all devices in the design

    if not (devices := Device.registry_items(subclasses=True)):
        log.warning(f"No devices found in this design, check config-file.")
        return

    # Ensure that all devices have a product_model assigned.  From these devices
    # form the unique set of product_model values so that these definitions can
    # be fetched from their origin source (i.e. Netbox)

    # TODO: should move this block of code to "validate device models" so that
    #       it can be resused in other activities.

    errors = 0
    product_models = set()
    for name, each_device in devices.items():
        if not each_device.product_model:
            log.error(
                f'Device missing product_model assignement: {name}'
            )
            errors += 1
            continue
        product_models.add(each_device.product_model)

    if errors:
        log.error(f"Errors: {errors}, aborting.")
        return

    # Run the processing in async model for performance benefits.

    asyncio.run(get_device_types(origin=origin_cls(),
                                 product_models=product_models))
