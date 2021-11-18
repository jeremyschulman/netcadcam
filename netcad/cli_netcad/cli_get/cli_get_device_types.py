# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import asyncio
import os

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.cli_netcad.main import clig_get
from netcad.config import netcad_globals, Environment
from netcad.init import loader
from netcad.device import Device
from netcad.origin import OriginDeviceType


# -----------------------------------------------------------------------------
# Exports (none)
# -----------------------------------------------------------------------------

__all__ = []

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@clig_get.command(name="device-types")
def clig_get_device_types():
    """
    Fetch the device product-model type definitions

    \b
    This command examines the device definitions for the declared
    product-models.  From that set of product module this command will then
    fetch the defintions from your SOT system, for example Netbox.
    """
    log = get_logger()

    os.environ[Environment.NETCAD_NOVALIDATE] = "1"

    modules = loader.import_designs_packages()
    loader.run_designs(modules)

    config = netcad_globals.g_config

    try:
        origin_name = config["get"]["device-types"]
        origin_package = config["origin"][origin_name]["package"]
        origin_cls = OriginDeviceType.import_origin(package=origin_package)

    except KeyError:
        raise RuntimeError(
            "Unable to find [get.device-types] in configuration file: "
            f"{netcad_globals.g_netcad_config_file.absolute()}"
        )

    # find all devices in the design

    if not (devices := Device.registry_items(subclasses=True)):
        log.warning(
            "No devices found in this design.  "
            f"Check config-file: {netcad_globals.g_netcad_config_file}"
        )
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
            log.error(f"Device missing product_model assignement: {name}")
            errors += 1
            continue
        product_models.add(each_device.product_model)

    if errors:
        log.error(f"Errors: {errors}, aborting.")
        return

    # Run the processing in async model for performance benefits.

    log.info(f"Fetching from {origin_name}, device-types: {','.join(product_models)}")

    asyncio.run(origin_cls.get(product_models=product_models))
