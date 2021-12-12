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
from netcad.testing_services import TestCases


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
    from netcad.netcam import CollectionTestResults


class _BaseDeviceUnderTest:
    def __init__(self, *, device: Device, testcases_dir: Path):
        self.device = device
        self.testcases_dir = testcases_dir
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

    def execute_testing(self):
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
    async def execute_testcases(
        self, testcases: TestCases
    ) -> Optional["CollectionTestResults"]:
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
