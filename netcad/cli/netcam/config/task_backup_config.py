#  Copyright (c) 2023 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from logging import Logger

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

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


async def backup_device_config(dev_cfg: AsyncDeviceConfigurable, log: Logger):
    name = dev_cfg.device.name
    log.info(f"{name}: Retrieving running configuration ...")
    filepath = await dev_cfg.backup()
    log.info(f"{name}: Backup saved to: {filepath}")
