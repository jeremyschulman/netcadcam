import os
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
from netcad.cli.netcam.netcam_filter_devices import netcam_filter_devices

from .config_main import clig_config
from .staged_config import SCPStagedConfig


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

        dev_cfg.config_dir = configs_dir / dev_obj.design.name
        dev_cfg.config_id = f"{dev_cfg.device.name}-{os.getpid()}-check"

        tasks.append(asyncio.create_task(check_device_config(dev_cfg, log)))

    await asyncio.gather(*tasks)


async def check_device_config(dev_cfg: AsyncDeviceConfigurable, log: Logger):
    name = dev_cfg.device.name
    basecfg_name = name + ".cfg"

    scp_cfg = SCPStagedConfig(
        dev_cfg=dev_cfg, config_file=Path(dev_cfg.config_dir / basecfg_name)
    )

    if await scp_cfg.stage():
        log.info(f"{name}: [green]OK[/green]: config-check passes")
    else:
        log.warning(f"{name}: [red]FAIL[/red]: config-check failed")

    # abort the staged config since this is a check action
    await scp_cfg.abort()
