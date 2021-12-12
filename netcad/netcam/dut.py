# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import AsyncGenerator, Optional, Dict
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


__all__ = ["DeviceUnderTest", "AsyncDeviceUnderTest"]


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
        async with aiofiles.open(str(self.testcases_dir / "device.json")) as ifile:
            payload = await ifile.read()
            self.device_info = json.loads(payload)

    @singledispatchmethod
    async def execute_testcases(self, testcases: TestCases) -> AsyncGenerator:
        raise NotImplementedError()

    async def teardown(self):
        raise NotImplementedError()
