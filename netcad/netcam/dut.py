from typing import AsyncGenerator
from functools import singledispatchmethod

from netcad.device import Device
from netcad.testing_services import TestCases


__all__ = ["DeviceUnderTest", "AsyncDeviceUnderTest"]


class _BaseDeviceUnderTest:
    def __init__(self, device: Device):
        self.device = device


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

    @singledispatchmethod
    async def execute_testcases(self, testcases: TestCases) -> AsyncGenerator:
        raise NotImplementedError()

    async def teardown(self):
        raise NotImplementedError()
