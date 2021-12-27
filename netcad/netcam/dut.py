#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Dict
from typing import TYPE_CHECKING
from functools import singledispatchmethod
from pathlib import Path
import json
from collections import Counter

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import aiofiles

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.checks import CheckCollection


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------


__all__ = ["DeviceUnderTest", "AsyncDeviceUnderTest"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

if TYPE_CHECKING:
    from netcad.netcam import CheckResultsCollection


class _BaseDeviceUnderTest:
    def __init__(self, *, device: Device):
        self.device = device
        self.testcases_dir: Optional[Path] = None
        self.device_info: Optional[Dict] = None
        self.result_counts = Counter()

    def __lt__(self, other):
        """
        Sort the device DUT instances by the underlying device hostname. This
        sort behavior overrides the underlying device "lt" override behavior as
        the purpose of DUT reporting is not specific to the arrangement of the
        devices in a design; but rather by the hostname value for User "eye
        sorting".
        """
        return self.device.name < other.device.name


class DeviceUnderTest(_BaseDeviceUnderTest):
    def setup(self):
        raise NotImplementedError()

    def execute_checks(self):
        raise NotImplementedError()

    def teardown(self):
        raise NotImplementedError()


class AsyncDeviceUnderTest(_BaseDeviceUnderTest):
    async def setup(self):
        """
        The default setup process is to load the "device info" testcases file so
        that the information contained in that file is available to any and all
        test case executors.  The subclassing plugin is expected to invoke this
        setup via super, and then perform any pluging/DUT specific setup action;
        generally opening a connection to the DUT API/SSH/etc.
        """
        async with aiofiles.open(str(self.testcases_dir / "device.json")) as ifile:
            payload = await ifile.read()
            self.device_info = json.loads(payload)

    @singledispatchmethod
    async def execute_checks(
        self, testcases: CheckCollection
    ) -> Optional["CheckResultsCollection"]:
        """
        The default testcase executor behavior will return None to indicate that
        the underlying plugin does not support the specific test-cases.
        """
        return None

    async def teardown(self):
        """
        There is no specific default behavior for the DUT teardown process.  The
        subclassing DUT generally uses this method to close/cleanup any specific
        resources that were created during the setup method.
        """
        pass
