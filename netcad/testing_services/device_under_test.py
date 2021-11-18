from pathlib import Path

from netcad.device import Device


__all__ = ["DeviceUnderTest", "AsyncDeviceUnderTest"]


class _BaseDeviceUnderTest:
    def __init__(self, device: Device, testcases_dir: Path):
        self.device = device
        self.testcases_dir = testcases_dir


class DeviceUnderTest(_BaseDeviceUnderTest):
    def setup(self):
        raise NotImplementedError()

    def execute_testing(self):
        raise NotImplementedError()

    def teardown(self):
        raise NotImplementedError()


class AsyncDeviceUnderTest(_BaseDeviceUnderTest):
    async def setup(self):
        raise NotImplementedError()

    async def execute_testing(self):
        raise NotImplementedError()

    async def teardown(self):
        raise NotImplementedError()
