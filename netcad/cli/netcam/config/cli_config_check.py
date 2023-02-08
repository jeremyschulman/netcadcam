import os
from typing import Tuple
from pathlib import Path
import asyncio
from logging import Logger

from asyncssh import SFTPError
import aiofiles
import aiofiles.os

from netcad.config import netcad_globals
from netcad.logger import get_logger
from netcad.device import Device, DeviceNonExclusive
from netcad.netcam.dev_config import AsyncDeviceConfigurable
from netcad.cli.device_inventory import get_devices_from_designs
from netcad.cli.common_opts import opt_devices, opt_designs, opt_configs_dir
from .config_main import clig_config
from netcad.cli.netcam.netcam_filter_devices import netcam_filter_devices


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
        tasks.append(asyncio.create_task(check_device_config(dev_cfg, log)))

    await asyncio.gather(*tasks)


async def check_device_config(dev_cfg: AsyncDeviceConfigurable, log: Logger):
    name = dev_cfg.device.name
    basecfg_name = name + ".cfg"

    # load the design config from the local filesystem so that we can load it
    # onto the device.

    lcl_cfg = Path(dev_cfg.config_dir / basecfg_name)

    config_id = f"{name}-{os.getpid()}-check"
    log.info(f"{name}: Loading configuration for check puroses only: id={config_id}")
    dev_cfg.config_id = config_id

    # if the device is not exclusively management by netcadcam, then
    # load the config using a "merge".  If it is exclusively management
    # by netcadcam the load the config using a "replace" opertation.

    replace = not isinstance(dev_cfg.device, DeviceNonExclusive)

    load_failed = False
    try:
        await dev_cfg.scp_config(lcl_cfg, dst_filename=basecfg_name)

    except OSError as exc:
        log.error(f"{name}: local file access failed: {str(exc)}")
        load_failed = True

    except SFTPError as exc:
        log.error(f"{name}: SCP failed: {str(exc)}")
        load_failed = True

    if load_failed:
        log.warning(f"{name}: aborting config-check")
        return

    try:
        await dev_cfg.load_scp_file(filename=basecfg_name, replace=replace)
    except Exception as exc:
        log.error(f"{name}: config-load failed: {str(exc)}")
        return

    try:
        config_diff = await dev_cfg.diff_config()

    except Exception as exc:
        log.error(f"{name}: diff-config failed: {str(exc)}")
        await dev_cfg.abort_config()
        return

    diffs_dir = dev_cfg.config_dir / "diffs"
    await aiofiles.os.makedirs(diffs_dir, exist_ok=True)

    async with aiofiles.open(diffs_dir / basecfg_name, "w+") as ofile:
        await ofile.write(config_diff)
        log.info(f"{name}: config-diff saved to: {ofile.name}")

    # discard the config since this is only a check.
    await dev_cfg.abort_config()
