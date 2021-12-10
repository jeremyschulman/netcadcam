# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import AsyncGenerator, Optional, Dict
from functools import singledispatchmethod
from pathlib import Path
import json

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
