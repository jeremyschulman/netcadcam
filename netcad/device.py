# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional, Dict
from collections import UserDict

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.port_profile import PortProfile
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


class DeviceInterfaces(UserDict):
    pass


class Device(object):
    product_model = None
    port_profiles: Optional[Dict[str, PortProfile]] = None
    interface_profiles = Optional[Dict[str, InterfaceProfile]] = None
    interfaces = DeviceInterfaces()

    def __init__(self, name: str):
        self.name = name


class RedundantPairDevices(object):
    def __init__(self, devices: List[Device]):
        pass
