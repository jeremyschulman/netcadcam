# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Type, Optional, Hashable, Dict, TypeVar, Iterable
from netcad.device import Device

# -----------------------------------------------------------------------------
# Pubic Imports
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.registry import Registry
from netcad.checks import CheckCollection

# -----------------------------------------------------------------------------
# Exports`
# -----------------------------------------------------------------------------

__all__ = ["DesignService", "DesignServiceCatalog", "DesignServiceLike"]


class DesignService(Registry, registry_name="design_services"):
    """
    A DesignService is a composition element within a Design.  Said another way,
    a Design is the composition of (collection of) DesignServices that the User
    wants to use to represent the operational state of their network.

    Attributes
    ----------
    name: str
        The User defined name of the Design service instance.  In many cases a
        sub-class of DesignService may default this value.  For example, the
        TopologyDesignService uses a name of "topology".

    devices: Set[Device]
        The collection of devices that are "using" this service.  Some
        DesignServices may be very specific to only a few devices in a Design.
        Other DesignServices may use all of the devices in a Design.  For
        example, the MLagDesginService would only include devices that are part
        of an MLAG arrangement.

    """

    def __init__(self, service_name: str, devices: Optional[Iterable[Device]] = None):
        """
        Superclass for create a new instance of a design service.  A Designer
        should not be calling this class directly, but rather a specific
        DesignService subclass, such as TopologyDesignService or
        VlanDesignService.

        Parameters
        ----------
        service_name: str
            The User defiined name of the service.  They can use this
            name to retrieve the service from the Design instance.

        devices: optional
            A collection of Device instances to add to this service. Devices can
            also be added via the `add_devices` method after the call to this
            init.
        """
        super().__init__()

        self.name = service_name
        self.devices = set()

        if devices:
            self.add_devices(*devices)

        self.testing_services: Optional[List[Type[CheckCollection]]] = list()

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
