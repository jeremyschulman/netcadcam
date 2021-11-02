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

from netcad.device import Device
from netcad.test_services import TestCases, TestCase
from netcad.test_services import testing_service

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
    interface: str


class InterfaceCablingTestCase(TestCase):
    test_params: InterfaceCablingTestParams
    expected_results: InterfaceCablingdExpectations

    def test_case_id(self) -> str:
        return str(self.test_params.interface)


@testing_service
class InterfaceCablingTestCases(TestCases):
    service = "cabling"
    tests: Optional[List[InterfaceCablingTestCase]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> "InterfaceCablingTestCases":

        # only used physical interfaces that have a cabling peer relationship.
        # exclude any interfaces that are disabled, since the cabling tests will
        # use a layer-2 protocol (LLDP or CDP) to validate the neighbor
        # relationship.

        interfaces = sorted(
            filter(
                lambda iface: iface.cable_peer and not iface.profile.is_virtual,
                device.interfaces.used(include_disabled=False).values(),
            )
        )

        test_cases = InterfaceCablingTestCases(
            exclusive=False,
            device=device.name,
            tests=[
                InterfaceCablingTestCase(
                    test_params=InterfaceCablingTestParams(interface=interface.name),
                    expected_results=InterfaceCablingdExpectations(
                        device=interface.cable_peer.device.name,
                        interface=interface.cable_peer.name,
                    ),
                )
                for interface in interfaces
            ],
        )

        return test_cases
