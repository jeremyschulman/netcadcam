#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import aiofiles

from netcad.logger import get_logger
from netcad.netcam.dev_config import AsyncDeviceConfigurable


from .deco_temp_file import temp_file

_OK_ = "[green]OK:[/green]"
_CHANGED_ = "[blue]CHANGED:[/blue]"
_FAIL_ = "[red]FAIL:[/red]"


@temp_file
async def push_device_config(dev_cfg: AsyncDeviceConfigurable, rollback_timeout: int):
    name = dev_cfg.device.name
    log = get_logger()
    log.info(f"{name}: deploying config ...")

    try:
        await dev_cfg.config_push(rollback_timeout=rollback_timeout)

    except RuntimeError as exc:
        log.error(str(exc))
        return

    if not dev_cfg.config_diff_contents:
        log.info(f"{name}: no config differences, nothig changed.")
        return

    log.info(f"{name}: config active and saved to startup")

    diff_file = dev_cfg.config_file.parent.joinpath("diffs") / dev_cfg.config_file.name
    async with aiofiles.open(diff_file, "w+") as ofile:
        log.info(f"{name}: saving config-diff: {ofile.name}")
        await ofile.write(dev_cfg.config_diff_contents)
