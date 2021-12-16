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

__all__ = ["TopologyService", "TopologyServiceLike"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class TopologyService(DesignService, registry_name="topology"):
    def __init__(self, network: str, name: Optional[str] = "topology"):

        # setup the design service with the User provided service name
        super(TopologyService, self).__init__(name=name)

        # register this topology by the User provided network name
        self.registry_add(name=network, obj=self)

        self.network = network
        self.cabling = CableByCableId(name=network)

        self.testing_services = [
            DeviceInformationTestCases,
            InterfaceTestCases,
            TransceiverTestCases,
            InterfaceCablingTestCases,
            LagTestCases,
            IPInterfacesTestCases,
        ]

    def add_devices(self, *devices: Device):
        super(TopologyService, self).add_devices(*devices)
        self.cabling.add_devices(*devices)

    def build(self):
        self.cabling.build()

    def validate(self):
        # TODO: put cabling validate here.
        pass


TopologyServiceLike = TypeVar("TopologyServiceLike", TopologyService, DesignService)
