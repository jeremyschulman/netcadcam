#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional, ClassVar

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, Field

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device, DeviceInterface
from netcad.checks import (
    CheckCollection,
    Check,
    CheckMeasurement,
    CheckResult,
    CheckExclusiveList,
    CheckExclusiveResult,
)
from ..topology_feature import TopologyDesignFeature

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "TransceiverCheckCollection",
    "TransceiverCheck",
    "TransceiverCheckResult",
    "TransceiverExclusiveListCheck",
    "TransceiverExclusiveListCheckResult",
]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class TransceiverCheck(Check):
    check_type: str = "transceiver"

    class Params(BaseModel):
        interface: str

    class Expect(BaseModel):
        model: str = (
            Field(
                ..., description="the transceiver product model name (vendor specific)"
            ),
        )
        type: str = Field(
            ..., description="the tranceiver physical type name (industry standard)"
        )

    check_params: Params
    expected_results: Expect

    def check_id(self) -> str:
        return str(self.check_params.interface)


class TransceiverCheckResult(CheckResult[TransceiverCheck]):
    class Measure(TransceiverCheck.Expect, CheckMeasurement):
        pass

    measurement: Measure = None


# -----------------------------------------------------------------------------#
# Exclusive list of interface transceivers
# -----------------------------------------------------------------------------#


class TransceiverExclusiveListCheck(Check):
    check_type: str = "transceivers-exclusive"
    expected_results: CheckExclusiveList[int]


class TransceiverExclusiveListCheckResult(
    CheckExclusiveResult[TransceiverExclusiveListCheck]
):
    class Measurement(CheckExclusiveList, CheckMeasurement):
        pass

    measurement: Measurement


# -----------------------------------------------------------------------------#
#
#                       The collection model
#
# -----------------------------------------------------------------------------#


@TopologyDesignFeature.register_check_collection
class TransceiverCheckCollection(CheckCollection):
    name: ClassVar[str] = "transceivers"
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
                check_params=TransceiverCheck.Params(interface=iface.name),
                expected_results=TransceiverCheck.Expect(
                    model=iface.profile.phy_profile.name, type=xcvr.type
                ),
            )

        return TransceiverCheckCollection(
            device=device.name,
            exclusive=not device.is_not_exclusive,
            checks=[_build_one_tc(iface) for iface in sorted(interfaces)],
        )
