# -----------------------------------------------------------------------------
# Systeme Imports
# -----------------------------------------------------------------------------

from typing import Optional, TypeVar
from copy import copy

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.cabling import CableByCableId
from netcad.design_services.design_service import DesignService

# -----------------------------------------------------------------------------
# Private Module Imports
# -----------------------------------------------------------------------------

from .check_transceivers import TransceiverCheckCollection
from .check_device_info import DeviceInformationCheckCollection
from .check_cabling_nei import InterfaceCablingCheckCollection
from .check_interfaces import InterfaceCheckCollection
from .check_lags import LagCheckCollection
from .check_ipaddrs import IpInterfacesCheckCollection

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["TopologyDesignService", "TopologyServiceLike"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class TopologyDesignService(DesignService, registry_name="topology"):
    """
    The TopologyDesignService is required for every design as it defines the set
    of devices, their interfaces, and the cabling-links that connect the
    device-interfaces.

    Attributes
    ----------
    name: str
        The topology name as defined by the Designer.  This name is typically
        the same name as the Design name; but it does not need to be.  This
        choice is up to the Designer.

    cabling: CableByCableId
        The cabling instance used to manage the relationship of the connected
        device interfaces.
    """

    CHECK_COLLECTIONS = [
        DeviceInformationCheckCollection,
        InterfaceCheckCollection,
        TransceiverCheckCollection,
        InterfaceCablingCheckCollection,
        LagCheckCollection,
        IpInterfacesCheckCollection,
    ]

    def __init__(
        self, topology_name: str, service_name: Optional[str] = "topology", **kwargs
    ):

        # The cabling must be created first becasue the add_devices, which is
        # called by the superclass constructor, uses cabling

        self.cabling = CableByCableId(name=topology_name)

        # setup the design service with the User provided service name

        super(TopologyDesignService, self).__init__(service_name=service_name, **kwargs)
        self.registry_add(name=topology_name, obj=self)
        self.topology_name = topology_name

        self.check_collections = copy(self.__class__.CHECK_COLLECTIONS)

    def add_devices(self, *devices: Device):
        super(TopologyDesignService, self).add_devices(*devices)
        self.cabling.add_devices(*devices)

    def build(self):
        self.cabling.build()

    def validate(self):
        # TODO: put cabling validate here.
        pass


TopologyServiceLike = TypeVar(
    "TopologyServiceLike", TopologyDesignService, DesignService
)
