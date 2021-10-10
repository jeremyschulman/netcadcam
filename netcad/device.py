# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List
from collections import UserDict, defaultdict
from operator import attrgetter

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device_interface import DeviceInterface

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

_DEVICE_REGISTRY = dict()


def get_device(name: str) -> "Device":
    return _DEVICE_REGISTRY.get(name)


class DevicePorts(UserDict):
    def __init__(self, device: "Device"):
        self.device = device
        super(DevicePorts, self).__init__()


class DeviceInterfaces(defaultdict):
    default_factory = DeviceInterface

    def __missing__(self, key):
        self[key] = self.default_factory(key)
        return self[key]


class Device(object):
    product_model = None
    template_file = None
    interfaces = DeviceInterfaces()

    def __init__(self, name: str):
        self.name = name
        _DEVICE_REGISTRY[self.name] = self

    def vlans(self):
        """return the set of VlanProfile instances used by this device"""

        vlans = set()

        for if_name, iface in self.interfaces.items():
            if not (if_prof := getattr(iface, "profile", None)):
                continue

            if get_vlans := getattr(if_prof, "if_vlans", None):
                vlans.update(get_vlans())

        return sorted(vlans, key=attrgetter("vlan_id"))


class RedundantPairDevices(object):
    def __init__(self, devices: List[Device]):
        pass
