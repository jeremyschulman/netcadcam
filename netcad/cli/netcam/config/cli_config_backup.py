from typing import Tuple
from pathlib import Path
import asyncio
from logging import Logger

from netcad.config import netcad_globals
from netcad.logger import get_logger
from netcad.device import Device
from netcad.netcam.dev_config import AsyncDeviceConfigurable
from netcad.cli.device_inventory import get_devices_from_designs
from netcad.cli.common_opts import opt_devices, opt_designs, opt_configs_dir
from .config_main import clig_config


@clig_config.command("backup")
@opt_devices()
@opt_designs()
@opt_configs_dir()
def cli_netcam_config_backup(
    devices: Tuple[str],
    designs: Tuple[str],
    configs_dir: Path,
):
    """
    Backup device configurations
    """
    log = get_logger()

    if not (device_objs := get_devices_from_designs(designs, include_devices=devices)):
        log.error("No devices located in the given designs")
        return

    device_objs = [dev for dev in device_objs if not dev.is_pseudo]
    asyncio.run(fetch_configs(configs_dir=configs_dir, device_objs=device_objs))


async def fetch_configs(device_objs: list[Device], configs_dir: Path):
    log = get_logger()

    netcam_plugins = netcad_globals.g_netcam_plugins_os_catalog
    dev_driver: dict[Device, AsyncDeviceConfigurable] = dict()

    dev_cfg: AsyncDeviceConfigurable
    tasks = list()

    for dev_obj in device_objs:
        if not (pg_obj := netcam_plugins.get(dev_obj.os_name)):
            raise RuntimeError(
                f"Missing testing plugin for {dev_obj.name}: os-name: {dev_obj.os_name}"
            )

        dev_driver[dev_obj] = dev_cfg = pg_obj.module.plugin_get_dcfg(device=dev_obj)
        # the device config(s) are stored within the design-name folder
        dev_cfg.config_dir = configs_dir / dev_obj.design.name / "backup"
        tasks.append(asyncio.create_task(backup(dev_cfg, log)))

    await asyncio.gather(*tasks)


async def backup(dev_cfg: AsyncDeviceConfigurable, log: Logger):
    name = dev_cfg.device.name
    log.info(f"{name}: Retrieving running configuration ...")
    filepath = await dev_cfg.backup()
    log.info(f"{name}: Backup saved to: {filepath}")
