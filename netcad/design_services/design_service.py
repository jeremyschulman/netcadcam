# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Type, Optional, Hashable, Dict
from netcad.device import Device

# -----------------------------------------------------------------------------
# Pubic Imports
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.registry import Registry
from netcad.testing_services import TestCases

# -----------------------------------------------------------------------------
# Exports`
# -----------------------------------------------------------------------------

__all__ = ["DesignService", "DesignServiceDirectory"]


class DesignService(Registry, registry_name="design_services"):
    def __init__(self, name: Hashable):
        super().__init__()
        self.registry_add(name, self)
        self.name = name
        self.devices = set()
        self.testing_services: Optional[List[Type[TestCases]]] = list()

    def add_devices(self, devices: List[Device]):
        """
        Add the list of devices to this design service.  Also add this service to each of the
        devices so that the devices have back-refernces to the service.

        Parameters
        ----------
        devices: list[Device]
            The list of device instances that will be associated to this design
            service.
        """
        self.devices.update(devices)
        for each_dev in devices:
            each_dev.services[self.name] = self

    async def build(self):
        """
        Peforms any build related algorithms necessary to implement the build
        process. This method is async so that underlying implementations can
        perform integrations with any other system.
        """
        raise NotImplementedError()

    async def validate(self):
        raise NotImplementedError()


DesignServiceDirectory = Dict[Hashable, DesignService]
