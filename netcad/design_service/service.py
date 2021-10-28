# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List

# -----------------------------------------------------------------------------
# Pubic Imports
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.registry import Registry
from netcad.device import Device

# -----------------------------------------------------------------------------
# Exports`
# -----------------------------------------------------------------------------

__all__ = ["DesignerService"]


class DesignerService(Registry):
    register_name = "designer_service"

    def __init__(self):
        self.devices = set()

    def add_devices(self, devices: List[Device]):
        self.devices.update(devices)

    async def build(self):
        """
        Peforms any build related algorithms necessary to implement the build
        process. This method is async so that underlying implementations can
        perform integrations with any other system.
        """
        raise NotImplementedError()

    async def validate(self):
        raise NotImplementedError()

    async def generate_tests(self, device: Device):
        raise NotImplementedError()
