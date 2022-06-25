#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional, Union, Literal

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, PositiveInt

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device, DeviceInterface
from netcad.checks import (
    CheckCollection,
    Check,
    CheckResult,
    CheckExclusiveResult,
    Measurement,
)
from netcad.checks import register_collection

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "InterfaceCheckCollection",
    "InterfaceCheck",
    "InterfaceCheckResult",
    "InterfaceCheckMeasurement",
    "InterfaceCheckParams",
    "InterfaceCheckUsedExpectations",
    "InterfaceCheckNotUsedExpectations",
    "InterfaceExclusiveListCheck",
    "InterfacesListExpected",
    "InterfaceExclusiveListCheckResult",
]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class InterfaceCheckParams(BaseModel):
    interface: str
    interface_flags: Optional[dict]


class InterfaceCheckUsedExpectations(BaseModel):
    used: Literal[True]
    desc: str
    oper_up: Optional[bool]
    speed: Optional[PositiveInt]


class InterfaceCheckNotUsedExpectations(BaseModel):
    used: Literal[False]


class InterfaceCheck(Check):
    check_type = "interface"

    check_params: InterfaceCheckParams
    expected_results: Union[
        InterfaceCheckUsedExpectations, InterfaceCheckNotUsedExpectations
    ]

    def check_id(self) -> str:
        return str(self.check_params.interface)


class InterfaceCheckMeasurement(Measurement):
    used: bool
    desc: str
    oper_up: bool
    speed: PositiveInt


class InterfaceCheckResult(CheckResult):
    measurement: InterfaceCheckMeasurement = None


# -----------------------------------------------------------------------------
# Check for exclusive list of interfaces on the device
# -----------------------------------------------------------------------------


class InterfacesListExpected(BaseModel):
    __root__: List[str]


class InterfacesListExpectedMesurement(InterfacesListExpected, Measurement):
    pass


class InterfaceExclusiveListCheckResult(CheckExclusiveResult):
    measurement: InterfacesListExpectedMesurement = None


class InterfaceExclusiveListCheck(Check):
    check_type = "exclusive"
    expected_results: InterfacesListExpected


# -----------------------------------------------------------------------------
#
#                         Interface Checks Collection
#
# -----------------------------------------------------------------------------


@register_collection
class InterfaceCheckCollection(CheckCollection):
    name = "interfaces"
    checks: Optional[List[InterfaceCheck]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> "InterfaceCheckCollection":
        def build_check(iface: DeviceInterface):

            # if the interface is not used, meaning it is not part of the
            # design, then there is no profile, and .enabled=False.  No other
            # interface valiation is required for operational state.

            if not iface.used:
                expected_results = InterfaceCheckNotUsedExpectations(used=False)
                if_flags = None

            # if the interface is used (in design) it still could be shutdown
            # (.enabled=False). we would still want to check the reporting speed
            # and descriptions as defined.

            else:
                port_profile = iface.profile.phy_profile
                if_flags = iface.profile.profile_flags

                expected_results = InterfaceCheckUsedExpectations(
                    used=True,
                    desc=iface.desc,
                    oper_up=iface.enabled,
                    speed=port_profile.speed if port_profile else None,
                )

                if iface.profile.is_reserved:
                    expected_results.oper_up = None

            return InterfaceCheck(
                check_params=InterfaceCheckParams(
                    interface=iface.name, interface_flags=if_flags
                ),
                expected_results=expected_results,
            )

        collection = InterfaceCheckCollection(
            device=device.name,
            exclusive=not device.is_not_exclusive,
            checks=[
                build_check(iface=interface)
                for if_name, interface in device.interfaces.items()
            ],
        )

        # if in non-exclusive mode, then only check the interfaces that are
        # defined as USED in the design.  Otherwise, the checks will include to
        # validate the UNUSED interfaces.

        if not collection.exclusive:
            collection.checks = [
                check
                for check in collection.checks
                if check.expected_results.used is True
            ]

        # return the checks sorted by the lag interface name
        collection.checks.sort(
            key=lambda tc: DeviceInterface(
                tc.check_params.interface, interfaces=device.interfaces
            )
        )
        return collection
