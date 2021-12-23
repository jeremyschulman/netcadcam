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
    "InterfaceCablingTestCases",
    "InterfaceCablingTestCase",
    "InterfaceCablingdExpectations",
    "InterfaceCablingTestParams",
]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class InterfaceCablingTestParams(BaseModel):
    interface: str


class InterfaceCablingdExpectations(BaseModel):
    device: str
    port_id: str


class InterfaceCablingTestCase(Check):
    check_params: InterfaceCablingTestParams
    expected_results: InterfaceCablingdExpectations

    def check_id(self) -> str:
        return str(self.check_params.interface)


@design_checks
class InterfaceCablingTestCases(CheckCollection):
    service = "cabling"
    checks: Optional[List[InterfaceCablingTestCase]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> "InterfaceCablingTestCases":

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

        test_cases = InterfaceCablingTestCases(
            exclusive=False,
            device=device.name,
            checks=[
                InterfaceCablingTestCase(
                    check_params=InterfaceCablingTestParams(interface=interface.name),
                    expected_results=InterfaceCablingdExpectations(
                        device=interface.cable_peer.device.name,
                        port_id=interface.cable_peer.cable_port_id,
                    ),
                )
                for interface in interfaces
            ],
        )

        return test_cases
