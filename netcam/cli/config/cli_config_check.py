#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
from typing import Tuple
from pathlib import Path
import asyncio

from netcad.config import netcad_globals
from netcad.logger import get_logger
from netcad.device import Device, DeviceNonExclusive
from netcam.dev_config import AsyncDeviceConfigurable
from netcad.cli.device_inventory import get_devices_from_designs
from netcad.cli.common_opts import opt_devices, opt_designs, opt_configs_dir
from netcam.cli.netcam_filter_devices import netcam_filter_devices

from .config_main import clig_config
from .task_config_check import check_device_config


@clig_config.command("check")
@opt_devices()
@opt_designs()
@opt_configs_dir()
def cli_netcam_config_backup(
    devices: Tuple[str],
    designs: Tuple[str],
    configs_dir: Path,
):
    """
    Given the built configuration, check that it will load and save the diff.
    """
    log = get_logger()

    if not (device_objs := get_devices_from_designs(designs, include_devices=devices)):
        log.error("No devices located in the given designs")
        return

    use_device_objs = netcam_filter_devices(device_objs)
    asyncio.run(run_check_configs(configs_dir=configs_dir, device_objs=use_device_objs))


async def run_check_configs(device_objs: list[Device], configs_dir: Path):
    log = get_logger()

    netcam_plugins = netcad_globals.g_netcam_plugins_os_catalog

    dev_cfg: AsyncDeviceConfigurable
    tasks = list()

    for dev_obj in device_objs:
        if not (pg_obj := netcam_plugins.get(dev_obj.os_name)):
            log.warning(
                f"{dev_obj.name}: Missing config-plugin for os-name: {dev_obj.os_name}"
            )
            continue

        if (dev_cfg := pg_obj.module.plugin_get_dcfg(device=dev_obj)) is None:
            log.warning(
                f"{dev_obj.name}: Does not support configuration management, skipping."
            )
            continue

        if dev_cfg.capabilities == dev_cfg.Capabilities.none:
            log.warning(
                f"{dev_obj.name}: Does not support configuration management, skipping."
            )
            continue

        dev_cfg.config_file = (
            configs_dir / dev_obj.design.name / (dev_obj.name + ".cfg")
        )
        dev_cfg.config_id = f"{dev_cfg.device.name}-{os.getpid()}-check"

        # TODO: for now, we are usin the fact that the device in the design is
        #       either exclusive or non-exclusive to determine whether or not
        #       to check the config with replacing or merging the built config.

        dev_cfg.replace = not isinstance(dev_obj, DeviceNonExclusive)
        tasks.append(asyncio.create_task(check_device_config(dev_cfg)))

    # TODO: need to check for excpeitons
    await asyncio.gather(*tasks)
