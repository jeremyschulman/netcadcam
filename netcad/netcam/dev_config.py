#  Copyright (c) 2023 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Tuple
from pathlib import Path
from enum import IntFlag, auto

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import asyncssh
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


class DeviceConfigurable:
    """
    Attributes
    ----------
    device: Device
        The design device instance for which this configurable is bound

    config_file: Path
        The local filesystem path to the proposed configuration file.

    config_diff_contents: str
        After the call to `config_diff` this attribute stores the device
        point-of-view diff; typically a diff-patch string.

    _config_id: str
        This value uniquely identifies the configuration.

        For transactional based systems, EOS and JUNOS for example, the value is
        used to name the "session" or "transaction".

        For non-transactional based systems the value could be used for
        purposes such as a remote-filename.  That said, this mode of
        device-configurable is not yet supported.

    _scp_creds: optional (str, str)
        Tuple that provides the (username, password) used for the SCP process.
        If this value is None, then SCP is not provided by the underlying
        device specific subclass.
    """

    class Capabilities(IntFlag):
        none = auto()

        # check implies that the OS supports a session or candidate configuration
        # that can be loaded but not activated; thus checking the validity
        # of the configuration syntax.

        check = auto()

        # diff means that the OS supports the ability to create a textual
        # difference between the proposed configuration and the current
        # configuration; without activating the proposed configuration.

        diff = auto()

        # replace means that the OS supports the ability to atomically replace
        # the running configuration with the proposed configuration.

        replace = auto()

        # rollback means that the OS supports the ability to automatically
        # rever the applied proposed configuration (which would be "now
        # active").  Rollback implies that the OS supports a timer-based
        # mechanism as well as a confirmation mechansim to cancel the rollback.

        rollback = auto()

        # merge means tha the OS driver will support loading config changes
        # that are not the complete configuration; also referred to as "merge
        # changes".  All operating systems support merges; but it is up to the
        # driver to deteremine whether to support it.

        merge = auto()

    def __init__(self, *, device: Device):
        self.device = device
        self.config_file: Optional[Path] = None
        self.config_diff_contents: Optional[str] = None
        self.file_on_device = False
        self.replace = False

        # subclass will set the capabilities on init
        self.capabilities = self.Capabilities.none

        # private attributes
        self._config_id: Optional[str] = None
        self._scp_creds: Optional[Tuple[str, str]] = None

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


class AsyncDeviceConfigurable(DeviceConfigurable):
    """
    Asynchronous based device-configurable supporting transaction based
    configuration changes.
    """

    async def setup(self):
        pass

    async def teardown(self):
        pass

    async def config_backup(self, backup_dir: Path) -> Path:
        """
        Retrieve the running configuration of the device and save it to the
        local filesystem in the given `backup_dir`.

        This method presumes that the `backup_dir` exists on the local
        filesystem. Otherwise, this function will raise an OSError exception as
        a result of attempting to saving the backup file.

        Returns
        -------
        The Path isntance of the backup file.
        """
        config_content = await self.config_get()
        backup_path = backup_dir / self.config_file.name

        async with aiofiles.open(backup_path, "w+") as ofile:
            await ofile.write(config_content)

        return backup_path

    # -------------------------------------------------------------------------
    #                     Abstract Private Methods
    # -------------------------------------------------------------------------

    def _set_config_id(self, name: str):
        raise NotImplementedError()

    async def is_reachable(self) -> bool:
        """
        Determines that the device is reachable for the purposes of making
        configuration chagnes.

        Returns
        -------
        True when the device is reachable, False otherwise.
        """
        raise NotImplementedError()

    # -------------------------------------------------------------------------
    # transactional config related methods
    # -------------------------------------------------------------------------

    async def config_get(self) -> str:
        """
        Retrieves the running configuration of a device as a text string.
        """
        raise NotImplementedError()

    async def config_cancel(self):
        """
        Cancel the configuration process for those devices that support
        staged / candidate configurations.
        """
        raise NotImplementedError()

    async def config_diff(self) -> str:
        """
        Retrieves the device point-of-view difference between the running
        configuraiton and the loaded configuration.  This assumes that the
        device can support this feature.

        After this call the `config_diff` attribute is set with the diff
        contents.

        Returns
        -------
        The "diff" output.  This will typically be in the form of a diff-patch;
        but it is device specific.
        """
        raise NotImplementedError()

    async def config_replace(self, rollback_timeout: int):
        """
        Replace the current running configuration with the candidate
        configuration file.   Once the candidate configuration is loaded check
        the device reachability.  If the reachability fails, then an exception
        is raised (TODO: type of exception).

        Parameters
        ----------
        rollback_timeout:
            The amount of time in minutes before the device automatically
            reverts to the previous running configuraiton.  This is a fail-safe
            mechanism in the even the loaded configuration breaks reachabilty
            to the device.
        """
        raise NotImplementedError()

    async def config_merge(self, rollback_timeout: int):
        """
        This function merges the candidate configuration into the running
        configuration.  If the device supports a rollback mechansim, the
        rollback_timeout designates time in minutes before the merged
        changes are reverted to the previous running config.

        Parameters
        ----------
        rollback_timeout:
            The amount of time in minutes before the device automatically
            reverts to the previous running configuraiton.  This is a fail-safe
            mechanism in the even the loaded configuration breaks reachabilty
            to the device.
        """
        raise NotImplementedError()

    async def config_push(
        self, rollback_timeout: int, replace: Optional[bool | None] = None
    ):
        """
        Push the configuration using the mode based on the `replace` option if
        set, or replace instance attribute.

        Parameters
        ----------
        rollback_timeout
        replace
        """
        replace = replace if replace is not None else self.replace

        if replace:
            await self.config_replace(rollback_timeout)
        else:
            await self.config_merge(rollback_timeout)

    async def config_check(self, replace: Optional[bool | None] = None) -> bool:
        raise NotImplementedError()

    # -------------------------------------------------------------------------
    # file related methods
    # -------------------------------------------------------------------------

    async def file_put(self, dst_filename: Optional[str | Path] = None):
        """
        This function copies the configuration file source_filepath from the
        local fileserver to the target device.  If the dst_filename is not
        given, then the basename of the source_filepath is used by default.
        """
        host = self.device.name

        if not self._scp_creds:
            raise RuntimeError(f"{host}: SCP credentials missing")

        username, password = self._scp_creds
        dst_fp = dst_filename or self.config_file.name
        async with asyncssh.connect(host, username=username, password=password) as conn:
            await asyncssh.scp(self.config_file, (conn, dst_fp))

        self.file_on_device = True

    async def file_delete(self):
        """
        This function is used to remove the configuration file that was
        previously copied to the remote device.  This function is expected to
        be called during a "cleanup" process.
        """
        raise NotImplementedError()
