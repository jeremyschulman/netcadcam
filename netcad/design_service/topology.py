# -----------------------------------------------------------------------------
# Systeme Imports
# -----------------------------------------------------------------------------

from typing import List

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.cabling import CableByCableId

from .service import DesignerService

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["TopologyService"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class TopologyService(DesignerService):
    def __init__(self, network: str):
        super(TopologyService, self).__init__()
        self.network = network
        self.cabling = CableByCableId(name=network)
        self.registry_add(name=network, obj=self)

    def add_devices(self, devices: List[Device]):
        super(TopologyService, self).add_devices(devices)
        self.cabling.add_devices(*devices)

    async def build(self):
        self.cabling.build()

    async def validate(self):
        pass

    async def generate_tests(self, device: Device):
        pass
