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
    "TransceiverTestCases",
    "TransceiverTestCase",
    "TransceiverTestParams",
    "TransceiverTestExpectations",
]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class TransceiverTestParams(BaseModel):
    interface: str


class TransceiverTestExpectations(BaseModel):
    model: str


class TransceiverTestCase(TestCase):
    test_params: TransceiverTestParams
    expected_results: TransceiverTestExpectations

    def test_case_id(self) -> str:
        return str(self.test_params.interface)


@testing_service
class TransceiverTestCases(TestCases):
    service = "transceivers"
    tests: Optional[List[TransceiverTestCase]]

    @classmethod
    def build(cls, device: Device) -> "TransceiverTestCases":

        # find all interfaces that have a designed transceiver assicated to the
        # interface profile -> port-profile.

        interfaces = [
            iface
            for iface in device.interfaces.iter_used().values()
            if iface.profile.port_profile and iface.profile.port_profile.transceiver
        ]

        return TransceiverTestCases(
            device=device.name,
            tests=[
                TransceiverTestCase(
                    test_params=TransceiverTestParams(interface=iface.name),
                    expected_results=TransceiverTestExpectations(
                        model=iface.profile.port_profile.name
                    ),
                )
                for iface in sorted(interfaces)
            ],
        )
