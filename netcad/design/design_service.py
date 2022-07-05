#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Type, Optional, Hashable, Dict, TypeVar, Iterable, Set

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device, DeviceNonExclusive
from netcad.registry import Registry
from netcad.checks import CheckCollection

from netcad.reporting import DesginReporting, ServiceReporting

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
        subclass of DesignService may default this value.  For example, the
        TopologyDesignService uses a name of "topology".

    devices: Set[Device]
        The collection of devices that are "using" this service.  Some
        DesignServices may be very specific to only a few devices in a Design.
        Other DesignServices may use all the devices in a Design.  For example,
        the MLagDesginService would only include devices that are part of an
        MLAG arrangement.

    exclusive: bool, optional
        When True it indicates that the design service checks should generate
        in exclusive mode.  When False indicates that the checks should not
        generate in exclusive mode.  When None the checks should defer to the
        device exclusivity mode.

    check_collections:
        The list of CheckCollection classes that will be used to validate this
        design service against the operatiional state of the network.
    """

    REPORTER = ServiceReporting

    def __init__(
        self,
        service_name: str,
        devices: Optional[Iterable[Device]] = None,
        exclusive: Optional[bool] = None,
    ):
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
        self.devices: Set[Device] = set()
        self.exclusive = exclusive

        if devices:
            self.add_devices(*devices)

        self.check_collections: List[Type[CheckCollection]] = list()

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

    def should_check_exclusively(self, device: Device) -> bool:
        """
        Returns True if the design check to build in "exclusive". If the
        service is explicitly configured, then that value will be used.
        Otherwise, the return value depends on if the device is declared as
        non-exclusive.
        """

        # if the service is not explicity configured, then use
        # the design of the device instance.

        if (exclusive := self.exclusive) is None:
            exclusive = not isinstance(device, DeviceNonExclusive)

        return exclusive

    def reporter(self, drg: DesginReporting) -> ServiceReporting:
        return self.REPORTER(drg=drg, service=self)


DesignServiceCatalog = Dict[Hashable, DesignService]
DesignServiceLike = TypeVar("DesignServiceLike", bound=DesignService)
