#  Copyright (c) 2023 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from pathlib import Path

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.netcam.dev_config import AsyncDeviceConfigurable

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["backup_device_config"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


async def backup_device_config(dev_cfg: AsyncDeviceConfigurable, backup_dir: Path):
    name = dev_cfg.device.name
    log = get_logger()
    log.info(f"{name}: Retrieving running configuration ...")

    try:
        filepath = await dev_cfg.config_backup(backup_dir)

    except RuntimeError as exc:
        log.error(str(exc))
        return

    log.info(f"{name}: Backup saved to: {filepath}")
