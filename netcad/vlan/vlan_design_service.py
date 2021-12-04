# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Set, Hashable, Optional, MutableMapping
from itertools import filterfalse
from operator import attrgetter
from collections import UserDict
from functools import lru_cache

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.design_services import DesignService

from .vlan_profile import VlanProfile

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["VlanDesignService", "DeviceVlanDesignService"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class DeviceVlanDesignService(DesignService):
    """
    The "Device Vlan" design service is used to manage the vlans on a per-device
    basis. This sevice, while all design services mataining a list of associated
    devices, has only one device.
    """

    def __init__(self, name: Hashable, device: Device):
        super().__init__(name=name)
        self.device = device
        self.add_devices([device])

    @lru_cache
    def vlans(self) -> List[VlanProfile]:
        """return the set of VlanProfile instances used by this device"""

        all_vlans: Set[VlanProfile] = set()
        interfaces = self.device.interfaces

        for if_name, iface in interfaces.used().items():

            if not (vlans_used := getattr(iface.profile, "vlans_used", None)):
                continue

            all_vlans.update(vlans_used())

        return sorted(all_vlans, key=attrgetter("vlan_id"))

    # -------------------------------------------------------------------------
    # Design Service required methods
    # -------------------------------------------------------------------------

    async def build(self):
        _ = self.vlans()

    async def validate(self):
        pass


class VlanDesignService(
    DesignService, UserDict, MutableMapping[Device, DeviceVlanDesignService]
):
    def __init__(
        self,
        name: Optional[Hashable] = "desgin_vlans",
        device_service_name: Optional[Hashable] = "vlans",
    ):

        super().__init__(name=name)
        self._device_service_name = device_service_name

    def add_devices(self, devices: List[Device]):
        super().add_devices(devices)
        for each_dev in filterfalse(lambda d: d in self.data, devices):
            self[each_dev] = DeviceVlanDesignService(
                name=self._device_service_name, device=each_dev
            )

    async def build(self):
        for each_dev in self.data.values():
            await each_dev.build()

    async def validate(self):
        pass
