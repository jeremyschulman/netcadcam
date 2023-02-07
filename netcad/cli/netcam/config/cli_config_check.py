import os
from typing import Tuple
from pathlib import Path
import asyncio
from logging import Logger

import aiofiles

from netcad.config import netcad_globals
from netcad.logger import get_logger
from netcad.device import Device, DeviceNonExclusive
from netcad.netcam.dev_config import AsyncDeviceConfigurable
from netcad.cli.device_inventory import get_devices_from_designs
from netcad.cli.common_opts import opt_devices, opt_designs, opt_configs_dir
from .config_main import clig_config
from .config_filter_devices import cli_config_filter_devices


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

    os.makedirs(configs_dir.joinpath("diffs"))

    use_device_objs = cli_config_filter_devices(device_objs, exclude_non_exclusive=True)
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

        dev_cfg.config_dir = configs_dir / dev_obj.design.name
        tasks.append(asyncio.create_task(check_device_config(dev_cfg, log)))

    await asyncio.gather(*tasks)


async def check_device_config(dev_cfg: AsyncDeviceConfigurable, log: Logger):
    name = dev_cfg.device.name

    # load the design config from the local filesystem so that we can load it
    # onto the device.

    async with aiofiles.open(dev_cfg.config_dir.joinpath(name + ".cfg")) as ifile:
        config_content = await ifile.read()

    config_id = f"{name}-{os.getpid()}-check"
    log.info(f"{name}: Loading configuration for check puroses only: id={config_id}")
    dev_cfg.config_id = config_id

    try:
        await dev_cfg.load_config(config_content, replace=True)
    except Exception as exc:
        breakpoint()
        x = 1

    config_diff = await dev_cfg.diff_config()
    async with aiofiles.open(dev_cfg.config_dir / "diffs" / (name + ".cfg")) as ofile:
        await ofile.write(config_diff)

    log.info(f"{name}: config-diff saved to: {ofile}")
    await dev_cfg.abort_config()
