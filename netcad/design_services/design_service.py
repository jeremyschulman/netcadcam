# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Type, Optional, Hashable, Dict, TypeVar
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

__all__ = ["DesignService", "DesignServiceCatalog", "DesignServiceLike"]


class DesignService(Registry, registry_name="design_services"):
    def __init__(self, name: Hashable):
        super().__init__()
        self.registry_add(name, self)
        self.name = name
        self.devices = set()
        self.testing_services: Optional[List[Type[TestCases]]] = list()

    def add_devices(self, *devices: Device):
        """
        Add the list of devices to this design service.  Also add this service to each of the
        devices so that the devices have back-refernces to the service.

        Parameters
        ----------
        devices:
            One or more Device instances to add to the design service.
        """

        self.devices.update(devices)
        for each_dev in devices:
            each_dev.services[self.name] = self

    def build(self):
        raise NotImplementedError()

    def validate(self):
        raise NotImplementedError()


DesignServiceCatalog = Dict[Hashable, DesignService]
DesignServiceLike = TypeVar("DesignServiceLike", bound=DesignService)
