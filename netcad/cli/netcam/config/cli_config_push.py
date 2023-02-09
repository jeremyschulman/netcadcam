import os
from typing import Tuple
from pathlib import Path
import asyncio
from datetime import timedelta

import click

from netcad.config import netcad_globals
from netcad.logger import get_logger
from netcad.device import Device
from netcad.netcam.dev_config import AsyncDeviceConfigurable
from netcad.cli.device_inventory import get_devices_from_designs
from netcad.cli.common_opts import opt_devices, opt_designs, opt_configs_dir
from netcad.cli.netcam.netcam_filter_devices import netcam_filter_devices

from .config_main import clig_config
from .task_push_config import push_device_config


@clig_config.command("push")
@opt_devices()
@opt_designs()
@opt_configs_dir()
@click.option(
    "--timeout-min",
    help="reachability timeout (minutes)",
    type=click.IntRange(min=1, max=5),
    default=1,
)
def cli_netcam_config_backup(
    devices: Tuple[str], designs: Tuple[str], configs_dir: Path, timeout_min: int
):
    """
    Deploy the design build configurations to device(s)
    """
    log = get_logger()

    if not (device_objs := get_devices_from_designs(designs, include_devices=devices)):
        log.error("No devices located in the given designs")
        return

    use_device_objs = netcam_filter_devices(device_objs)
    asyncio.run(
        run_deploy_configs(
            configs_dir=configs_dir,
            device_objs=use_device_objs,
            timeout=timedelta(minutes=timeout_min),
        )
    )


async def run_deploy_configs(
    device_objs: list[Device], configs_dir: Path, timeout: timedelta
):
    log = get_logger()

    netcam_plugins = netcad_globals.g_netcam_plugins_os_catalog

    dev_cfg: AsyncDeviceConfigurable

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
        dev_cfg.config_id = f"{dev_cfg.device.name}-{os.getpid()}"

        await push_device_config(dev_cfg, timeout=timeout)
