# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional
from collections import UserDict, defaultdict
from operator import attrgetter

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.interface_profile import InterfaceProfile

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


class DeviceInterface(object):
    profile: Optional[InterfaceProfile]
    used: Optional[bool] = True
    desc: Optional[str] = "UNUSED"

    def __repr__(self):
        if hasattr(self, "profile"):
            return self.profile.__class__.__name__

        if self.used is False:
            return "Unused"

        return super(DeviceInterface, self).__repr__()


class Device(object):
    product_model = None
    template_file = None
    interfaces = defaultdict(DeviceInterface)

    def __init__(self, name: str):
        self.name = name
        _DEVICE_REGISTRY[self.name] = self

    def vlans(self):
        """return the set of VlanProfile instances used by this device"""

        vlans = set()

        for if_name, iface in self.interfaces.items():
            if not (if_prof := getattr(iface, "profile", None)):
                continue

            if hasattr(if_prof, "profile_vlans"):
                vlans.update(if_prof.profile_vlans())

        return sorted(vlans, key=attrgetter("vlan_id"))


class RedundantPairDevices(object):
    def __init__(self, devices: List[Device]):
        pass
