# -----------------------------------------------------------------------------
# Systeme Imports
# -----------------------------------------------------------------------------

from typing import Optional, TypeVar

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.cabling import CableByCableId
from netcad.design_services.design_service import DesignService

# -----------------------------------------------------------------------------
# Private Module Imports
# -----------------------------------------------------------------------------

from .tc_transceivers import TransceiverTestCases
from .tc_device_info import DeviceInformationTestCases
from .tc_cabling_nei import InterfaceCablingTestCases
from .tc_interfaces import InterfaceTestCases
from .tc_lags import LagTestCases
from .tc_ipaddrs import IPInterfacesTestCases

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
    """

    DESIGN_CHECKS = [
        DeviceInformationTestCases,
        InterfaceTestCases,
        TransceiverTestCases,
        InterfaceCablingTestCases,
        LagTestCases,
        IPInterfacesTestCases,
    ]

    def __init__(self, name: str, service_name: Optional[str] = "topology", **kwargs):

        # The cabling must be created first becasue the add_devices, which is
        # called by the superclass constructor, uses cabling

        self.cabling = CableByCableId(name=name)

        # setup the design service with the User provided service name

        super(TopologyDesignService, self).__init__(service_name=service_name, **kwargs)

        self.registry_add(name=name, obj=self)
        self.name = name

        # TODO: cleanup the use/naming of "testing" vs. "checks"
        self.testing_services = [
            DeviceInformationTestCases,
            InterfaceTestCases,
            TransceiverTestCases,
            InterfaceCablingTestCases,
            LagTestCases,
            IPInterfacesTestCases,
        ]

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
