# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional
from collections import UserDict, defaultdict

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


class DevicePorts(UserDict):
    def __init__(self, device: "Device"):
        self.device = device
        super(DevicePorts, self).__init__()


class DeviceInterface(object):
    profile: Optional[InterfaceProfile]
    used: Optional[bool] = True
    desc: Optional[str] = "UNUSED"


class Device(object):
    product_model = None
    interfaces = defaultdict(DeviceInterface)

    def __init__(self, name: str):
        self.name = name


class RedundantPairDevices(object):
    def __init__(self, devices: List[Device]):
        pass
