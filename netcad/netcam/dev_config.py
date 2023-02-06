#  Copyright (c) 2023 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Dict
from pathlib import Path

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import aiofiles
import aiofiles.os

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["AsyncDeviceConfigurable"]


class _BaseDeviceConfigurable:
    def __init__(self, *, device: Device):
        self.device = device
        self.config_dir: Optional[Path] = None
        self.device_info: Optional[Dict] = None

    def __lt__(self, other):
        """
        Sort the device DUT instances by the underlying device hostname. This
        sort behavior overrides the underlying device "lt" override behavior as
        the purpose of DUT reporting is not specific to the arrangement of the
        devices in a design; but rather by the hostname value for User "eye
        sorting".
        """
        return self.device.name < other.device.name


class AsyncDeviceConfigurable(_BaseDeviceConfigurable):
    async def fetch_running_config(self) -> str:
        """
        Retrieves the running configuration of a device as a single text string.
        """
        raise NotImplementedError()

    async def backup(self) -> Path:
        config_content = await self.fetch_running_config()
        path = Path(self.config_dir).joinpath(self.device.name + ".cfg")
        await aiofiles.os.makedirs(self.config_dir, exist_ok=True)
        async with aiofiles.open(path, "w+") as ofile:
            await ofile.write(config_content)

        return path
