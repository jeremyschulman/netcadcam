#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple
import asyncio
import os

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.config import netcad_globals, Environment
from netcad.device import Device
from netcad.origin import OriginDeviceType

from netcad.cli.netcad.cli_netcad_main import clig_get
from ..device_inventory import get_devices_from_designs
from ..common_opts import opt_devices, opt_designs

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
@opt_designs(required=True)
@opt_devices()
def clig_get_device_types(devices: Tuple[str], designs: Tuple[str]):
    """
    Fetch the device product-model type definitions

    \b
    This command examines the device definitions for the declared
    product-models.  From that set of product module this command will then
    fetch the defintions from your SOT system, for example Netbox.
    """
    log = get_logger()

    os.environ[Environment.NETCAD_NOVALIDATE] = "1"
    get_devices_from_designs(designs=designs, include_devices=devices)

    config = netcad_globals.g_config

    try:
        origin_name = config["get"]["device-types"]
        origin_package = config["origin"][origin_name]["package"]
        origin_cls = OriginDeviceType.import_origin(package=origin_package)

    except KeyError:
        raise RuntimeError(
            "Configuration file error: missing "
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

    log.info(f"Fetching from {origin_name}, {len(product_models)} device-types")
    asyncio.run(origin_cls.get(product_models=product_models))
