#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

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
from netcad.checks import CheckCollection, Check, CheckExclusiveResult, CheckMeasurement
from netcad.checks import register_collection

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "TransceiverCheckCollection",
    "TransceiverCheck",
    "TransceiverCheckParams",
    "TransceiverCheckExpectations",
    "TransceiverExclusiveListCheck",
    "TransceiverExclusiveListCheckResult",
]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class TransceiverCheckParams(BaseModel):
    interface: str


class TransceiverCheckExpectations(BaseModel):
    model: str  # the transceiver product model name (vendor specific)
    type: str  # the tranceiver physical type name (industry standard)


class TransceiverCheck(Check):
    check_type = "transceiver"
    check_params: TransceiverCheckParams
    expected_results: TransceiverCheckExpectations

    def check_id(self) -> str:
        return str(self.check_params.interface)


# -----------------------------------------------------------------------------#
# Exclusive list of interface transceivers
# -----------------------------------------------------------------------------#


class TransceiverListExpected(BaseModel):
    __root__: List[int]


class TransceiverExclusiveListCheck(Check):
    check_type = "transceivers-exclusive"
    expected_results: TransceiverListExpected


class TransceiverListMeasurement(TransceiverListExpected, CheckMeasurement):
    pass


class TransceiverExclusiveListCheckResult(CheckExclusiveResult):
    check: TransceiverExclusiveListCheck
    measurement: TransceiverListMeasurement


# -----------------------------------------------------------------------------#
#
#                       The collection model
#
# -----------------------------------------------------------------------------#


@register_collection
class TransceiverCheckCollection(CheckCollection):
    name = "transceivers"
    checks: Optional[List[TransceiverCheck]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> "TransceiverCheckCollection":

        # find all interfaces that have a designed transceiver assicated to the
        # interface profile -> port-profile.

        interfaces = [
            iface
            for iface in device.interfaces.used().values()
            if iface.profile.phy_profile and iface.profile.phy_profile.transceiver
        ]

        def _build_one_tc(iface: DeviceInterface):
            port_profile = iface.profile.phy_profile
            xcvr = port_profile.transceiver

            return TransceiverCheck(
                check_params=TransceiverCheckParams(interface=iface.name),
                expected_results=TransceiverCheckExpectations(
                    model=iface.profile.phy_profile.name, type=xcvr.type
                ),
            )

        return TransceiverCheckCollection(
            device=device.name,
            exclusive=not device.is_not_exclusive,
            checks=[_build_one_tc(iface) for iface in sorted(interfaces)],
        )
