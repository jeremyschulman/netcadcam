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
    """
    Attributes
    ----------
    device: Device
        The design device instance for which this configurable is bound

    config_dir: Path
        The local filesystem directory for which the device configuraiton will
        be loaded from.  The backup configuration will be stored in
        subdirectory called "backup".

    _config_id: str
        This value uniquely identifies the configuration.

        For transactional based systems, EOS and JUNOS for example, the value is
        used to name the "session" or "transaction".

        For non-transactional based systems the value could be used for
        purposes such as a remote-filename.  That said, this mode of
        device-configurable is not yet supported.
    """

    def __init__(self, *, device: Device):
        self.device = device
        self.config_dir: Optional[Path] = None
        self._config_id: Optional[str] = None

    @property
    def config_id(self):
        return self._config_id

    @config_id.setter
    def config_id(self, name: str):
        self._set_config_id(name)
        self._config_id = name

    def _set_config_id(self, name: str):
        raise NotImplementedError()

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
    """
    Asynchronous based device-configurable supporting transaction based
    configuration changes.
    """

    def _set_config_id(self, name: str):
        raise NotImplementedError()

    async def check_reachability(self) -> bool:
        """
        Determines that the device is reachable for the purposes of making
        configuration chagnes.

        Returns
        -------
        True when the device is reachable, False otherwise.
        """
        raise NotImplementedError()

    async def fetch_running_config(self) -> str:
        """
        Retrieves the running configuration of a device as a text string.
        """
        raise NotImplementedError()

    async def abort_config(self):
        """
        Aborts the staged configuration.
        """
        raise NotImplementedError()

    async def diff_config(self) -> str:
        """
        Retrieves the device point-of-view difference between the running
        configuraiton and the loaded configuration.  This assumes that the
        device can support this feature.

        Returns
        -------
        The "diff" output.  This will typically be in the form of a diff-patch;
        but it is device specific.
        """
        raise NotImplementedError()

    async def load_config(self, config_contents: str, replace: Optional[bool] = False):
        """
        Loads the contents of the configuration onto the device.  If the
        replace parameter is True, then the contents completely replace the
        configuration. Otherwise, the changes are loaded in a "merge" style.

        Parameters
        ----------
        config_contents:
            The configuration to load into the device

        replace:
            When True the config_contents replace the entirety of the device configuration.
        """
        raise NotImplementedError()

    async def backup(self) -> Path:
        """
        Retrieve the running configuration of the device and save it to the
        local backup filesystem.

        Returns
        -------
        The Path isntance of the backup file.
        """
        config_content = await self.fetch_running_config()
        path = Path(self.config_dir).joinpath(self.device.name + ".cfg")
        await aiofiles.os.makedirs(self.config_dir, exist_ok=True)
        async with aiofiles.open(path, "w+") as ofile:
            await ofile.write(config_content)

        return path
