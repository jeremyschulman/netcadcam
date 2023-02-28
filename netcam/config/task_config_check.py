#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import aiofiles

from netcad.logger import get_logger
from netcam.dcfg import AsyncDeviceConfigurable
from netcam.config.deco_temp_file import temp_file

_OK_ = "[green]OK:[/green]"
_CHANGED_ = "[blue]CHANGED:[/blue]"
_FAIL_ = "[red]FAIL:[/red]"


__all__ = ["check_device_config"]


@temp_file
async def check_device_config(dev_cfg: AsyncDeviceConfigurable):
    name = dev_cfg.device.name
    log = get_logger()

    # -------------------------------------------------------------------------
    # Run the config check based on the capabiltiies of the device driver
    # -------------------------------------------------------------------------

    if dev_cfg.Capabilities.check in dev_cfg.capabilities:
        log.info(f"{name}: config-check ...")

        if errors := await dev_cfg.config_check():
            log.warning(f"{name}: {_FAIL_} config-check failed: {errors}")
        else:
            log.info(f"{name}: {_OK_} config-check passes.")

        config_diff = dev_cfg.config_diff_contents

    elif dev_cfg.Capabilities.diff in dev_cfg.capabilities:
        log.info(f"{name}: config-diff ...")
        config_diff = await dev_cfg.config_diff()

    else:
        log.error(f"{name}: Unexpected missing capabilities")
        return

    # -------------------------------------------------------------------------
    # handle any diffs recorded by the config-check.
    # -------------------------------------------------------------------------

    if not config_diff:
        log.info(f"{name}: no config differences")
        return

    diff_file = dev_cfg.config_file.parent.joinpath("diffs") / dev_cfg.config_file.name
    async with aiofiles.open(diff_file, "w+") as ofile:
        log.info(f"{name}: saving config-diff: {ofile.name}")
        await ofile.write(config_diff)
