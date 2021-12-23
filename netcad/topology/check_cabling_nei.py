# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device, DeviceInterface
from netcad.checks import CheckCollection, Check
from netcad.checks import design_checks

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "InterfaceCablingCheckCollection",
    "InterfaceCablingCheck",
    "InterfaceCablingdExpectations",
    "InterfaceCablingCheckParams",
]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class InterfaceCablingCheckParams(BaseModel):
    interface: str


class InterfaceCablingdExpectations(BaseModel):
    device: str
    port_id: str


class InterfaceCablingCheck(Check):
    check_params: InterfaceCablingCheckParams
    expected_results: InterfaceCablingdExpectations

    def check_id(self) -> str:
        return str(self.check_params.interface)


@design_checks
class InterfaceCablingCheckCollection(CheckCollection):
    service = "cabling"
    checks: Optional[List[InterfaceCablingCheck]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> "InterfaceCablingCheckCollection":

        # only used physical interfaces that have a cabling peer relationship.
        # exclude any interfaces that are disabled, since the cabling tests will
        # use a layer-2 protocol (LLDP or CDP) to validate the neighbor
        # relationship.

        interfaces: List[DeviceInterface] = sorted(
            filter(
                lambda iface: iface.cable_peer and not iface.profile.is_virtual,
                device.interfaces.used(include_disabled=False).values(),
            )
        )

        return InterfaceCablingCheckCollection(
            exclusive=False,
            device=device.name,
            checks=[
                InterfaceCablingCheck(
                    check_params=InterfaceCablingCheckParams(interface=interface.name),
                    expected_results=InterfaceCablingdExpectations(
                        device=interface.cable_peer.device.name,
                        port_id=interface.cable_peer.cable_port_id,
                    ),
                )
                for interface in interfaces
            ],
        )
