from typing import List

from collections import UserDict


class DevicePort(object):
    def __init__(self, name: str, device: "Device"):
        self.name = name
        self.device = device


class DevicePorts(UserDict):
    pass


class Device(object):
    def __init__(self, name: str):
        self.name = name
        self.ports = DevicePorts()


class RedundantPairDevices(object):
    def __init__(self, devices: List[Device]):
        pass
