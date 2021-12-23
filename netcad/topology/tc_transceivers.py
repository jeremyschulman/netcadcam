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
    "TransceiverTestCases",
    "TransceiverTestCase",
    "TransceiverTestParams",
    "TransceiverTestExpectations",
    "TransceiverListTestCase",
]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class TransceiverTestParams(BaseModel):
    interface: str


class TransceiverTestExpectations(BaseModel):
    model: str  # the transceiver product model name (vendor specific)
    type: str  # the tranceiver physical type name (industry standard)


class TransceiverTestCase(Check):
    check_params: TransceiverTestParams
    expected_results: TransceiverTestExpectations

    def check_id(self) -> str:
        return str(self.check_params.interface)


class TransceiverListTestCase(Check):
    def __init__(self, **kwargs):
        super().__init__(
            test_case="transceiver-list",
            test_params=BaseModel(),
            expected_results=BaseModel(),
            **kwargs
        )

    def check_id(self) -> str:
        return "exclusive_list"


@design_checks
class TransceiverTestCases(CheckCollection):
    service = "transceivers"
    checks: Optional[List[TransceiverTestCase]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> "TransceiverTestCases":

        # find all interfaces that have a designed transceiver assicated to the
        # interface profile -> port-profile.

        interfaces = [
            iface
            for iface in device.interfaces.used().values()
            if iface.profile.port_profile and iface.profile.port_profile.transceiver
        ]

        def _build_one_tc(iface: DeviceInterface):
            port_profile = iface.profile.port_profile
            xcvr = port_profile.transceiver

            return TransceiverTestCase(
                check_params=TransceiverTestParams(interface=iface.name),
                expected_results=TransceiverTestExpectations(
                    model=iface.profile.port_profile.name, type=xcvr.type
                ),
            )

        return TransceiverTestCases(
            device=device.name,
            checks=[_build_one_tc(iface) for iface in sorted(interfaces)],
        )
