#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional, Union, Literal, ClassVar

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, NonNegativeInt, RootModel

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device, DeviceInterface
from netcad.checks import (
    CheckCollection,
    Check,
    CheckResult,
    CheckExclusiveResult,
    CheckMeasurement,
)
from ..topology_feature import TopologyDesignFeature

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

# -----------------------------------------------------------------------------
# Single interface check
# -----------------------------------------------------------------------------


class InterfaceCheckParams(BaseModel):
    interface: str
    interface_flags: Optional[dict]


class InterfaceCheckUsedExpectations(BaseModel):
    """For when an interface IS used"""

    used: Literal[True]
    desc: str
    oper_up: Optional[bool]
    speed: Optional[NonNegativeInt]


class InterfaceCheckNotUsedExpectations(BaseModel):
    """For when an interface is NOT used"""

    used: Literal[False]


class InterfaceCheck(Check):
    check_type: str = "interface"

    check_params: InterfaceCheckParams
    expected_results: Union[
        InterfaceCheckUsedExpectations, InterfaceCheckNotUsedExpectations
    ]

    def check_id(self) -> str:
        return str(self.check_params.interface)


class InterfaceCheckMeasurement(CheckMeasurement):
    """
    The measurement fields are a copy-paste since we cannot subclass both used
    and unused classes together given the use of the Literal marker.
    """

    used: bool
    desc: str
    oper_up: bool
    speed: NonNegativeInt


class InterfaceCheckResult(CheckResult):
    check: InterfaceCheck
    measurement: InterfaceCheckMeasurement = None


# -----------------------------------------------------------------------------
# Check for exclusive list of interfaces on the device
# -----------------------------------------------------------------------------


class InterfacesListExpected(RootModel):
    root: List[str]


class InterfacesListExpectedMesurement(InterfacesListExpected, CheckMeasurement):
    pass


class InterfaceExclusiveListCheck(Check):
    check_type: str = "interfaces-exclusive"
    check_params: Optional[BaseModel] = None
    expected_results: InterfacesListExpected


class InterfaceExclusiveListCheckResult(CheckExclusiveResult):
    check: InterfaceExclusiveListCheck
    measurement: InterfacesListExpectedMesurement = None


# -----------------------------------------------------------------------------
#
#                         Interface Checks Collection
#
# -----------------------------------------------------------------------------


@TopologyDesignFeature.register_check_collection
class InterfaceCheckCollection(CheckCollection):
    name: ClassVar[str] = "interfaces"
    checks: Optional[List[InterfaceCheck]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> "InterfaceCheckCollection":
        def build_check(iface: DeviceInterface):
            # if the interface is not used, meaning it is not part of the
            # design, then there is no profile.  No other interface valiation
            # is required for operational state.

            if not iface.used:
                expected_results = InterfaceCheckNotUsedExpectations(used=False)
                if_flags = None

            # if the interface is used (in design) it still could be shutdown
            # (.enabled=False). we would still want to check the reporting speed
            # and descriptions as defined.

            else:
                port_profile = iface.profile.phy_profile
                if_flags = iface.profile.profile_flags

                # -------------------------------------------------------------
                # adding a feature that allows for a design to explicitly
                # transition an interface to the unused state.
                # -------------------------------------------------------------
                # The designer would need to assisgn the interface profile the
                # same class instance as the device unused_interface_profile.
                # When this is the case then a check will be generated to
                # verify that the port is shutdown and any associated interface
                # description in the interface profile instance is collected
                # and checked.  We add a new interface flag for this purpose to
                # let the check generator (later) and underlying "netcam"
                # drivers know of this specific case.

                is_forced_unused = isinstance(
                    iface.profile, device.unused_interface_profile.__class__
                )
                if is_forced_unused:
                    if_flags["is_forced_unused"] = True

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
                if (check.expected_results.used is True)
                or (
                    (if_flags := check.check_params.interface_flags)
                    and if_flags.get("is_forced_unused")
                )
            ]

        # return the checks sorted by the lag interface name
        collection.checks.sort(
            key=lambda tc: DeviceInterface(
                tc.check_params.interface, interfaces=device.interfaces
            )
        )
        return collection
