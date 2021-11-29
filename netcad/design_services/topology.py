# -----------------------------------------------------------------------------
# Systeme Imports
# -----------------------------------------------------------------------------

from typing import List

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.cabling import CableByCableId

from .design_service import DesignService
from netcad.testing_services import (
    device,
    interfaces,
    lags,
    vlans,
    transceivers,
    cabling,
    ipaddrs,
)

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["TopologyService"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class TopologyService(DesignService, registry_name="topology"):
    def __init__(self, network: str):
        super(TopologyService, self).__init__()
        self.network = network
        self.cabling = CableByCableId(name=network)
        self.registry_add(name=network, obj=self)

        self.testing_services = [
            device.DeviceInformationTestCases,
            interfaces.InterfaceTestCases,
            transceivers.TransceiverTestCases,
            vlans.VlanTestCases,
            cabling.InterfaceCablingTestCases,
            lags.LagTestCases,
            ipaddrs.IPInterfacesTestCases,
        ]

    def add_devices(self, devices: List[Device]):
        super(TopologyService, self).add_devices(devices)
        self.cabling.add_devices(devices)

    async def build(self):
        self.cabling.build()

    async def validate(self):
        pass
