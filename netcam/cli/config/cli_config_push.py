#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import os
from typing import Tuple
from pathlib import Path
import asyncio

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import click

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import netcad_globals
from netcad.logger import get_logger
from netcad.device import Device, DeviceNonExclusive
from netcam.dcfg import AsyncDeviceConfigurable
from netcad.cli.device_inventory import get_devices_from_designs
from netcad.cli.common_opts import opt_devices, opt_designs, opt_configs_dir
from netcam.cli.netcam_filter_devices import netcam_filter_devices

from .cli_config_main import clig_config
from netcam.config import push_device_config

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


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
@click.option("--concurrent", "-c", is_flag=True, help="Enable concurrent push")
def cli_netcam_config_backup(
    devices: Tuple[str],
    designs: Tuple[str],
    configs_dir: Path,
    timeout_min: int,
    concurrent: bool,
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
            rollback_timeout=timeout_min,
            concurrent=concurrent,
        )
    )


async def run_deploy_configs(
    device_objs: list[Device],
    configs_dir: Path,
    rollback_timeout: int,
    concurrent: bool,
):
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

        dev_cfg.config_file = (
            configs_dir / dev_obj.design.name / (dev_obj.name + ".cfg")
        )

        # TODO: for now, we are usin the fact that the device in the design is
        #       either exclusive or non-exclusive to determine whether or not
        #       to check the config with replacing or merging the built config.

        dev_cfg.replace = not isinstance(dev_obj, DeviceNonExclusive)
        dev_cfg.config_id = (
            f"netcam-{'replace' if dev_cfg.replace else 'merge'}-{os.getpid()}"
        )

        # TODO: need to check for exceptions
        tasks.append(push_device_config(dev_cfg, rollback_timeout=rollback_timeout))

    if concurrent:
        await asyncio.gather(*tasks)

    else:
        for task in tasks:
            await task
