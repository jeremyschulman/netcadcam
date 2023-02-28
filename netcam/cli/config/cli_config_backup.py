#  Copyright (c) 2023 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple
from pathlib import Path
import asyncio

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import netcad_globals
from netcad.logger import get_logger
from netcad.device import Device
from netcam.dcfg import AsyncDeviceConfigurable
from netcad.cli.device_inventory import get_devices_from_designs
from netcad.cli.common_opts import opt_devices, opt_designs, opt_configs_dir

from netcam.cli.netcam_filter_devices import netcam_filter_devices
from .config_main import clig_config
from netcam.config import backup_device_config

# -----------------------------------------------------------------------------
# Exports (None)
# -----------------------------------------------------------------------------

__all__ = []

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


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

    device_objs = netcam_filter_devices(device_objs)
    asyncio.run(run_fetch_configs(configs_dir=configs_dir, device_objs=device_objs))


async def run_fetch_configs(device_objs: list[Device], configs_dir: Path):
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

        cfg_site_dir = configs_dir / dev_obj.design.name
        cfg_backup_dir = cfg_site_dir / "backup"
        dev_cfg.config_file = configs_dir.joinpath(dev_obj.name + ".cfg")

        tasks.append(
            asyncio.create_task(
                backup_device_config(dev_cfg, backup_dir=cfg_backup_dir)
            )
        )

    await asyncio.gather(*tasks)
