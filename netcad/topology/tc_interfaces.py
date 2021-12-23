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
from netcad.checks import CheckCollection, Check
from netcad.checks import design_checks

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "InterfaceTestCases",
    "InterfaceTestCase",
    "InterfaceTestParams",
    "InterfaceTestUsedExpectations",
    "InterfaceTestNotUsedExpectations",
    "InterfaceListTestCase",
]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class InterfaceTestParams(BaseModel):
    interface: str
    interface_flags: Optional[dict]


class InterfaceTestUsedExpectations(BaseModel):
    used: Literal[True]
    oper_up: Optional[bool]
    desc: str
    speed: Optional[PositiveInt]


class InterfaceTestNotUsedExpectations(BaseModel):
    used: Literal[False]


class InterfaceTestCase(Check):
    check_params: InterfaceTestParams
    expected_results: Union[
        InterfaceTestUsedExpectations, InterfaceTestNotUsedExpectations
    ]

    def check_id(self) -> str:
        return str(self.check_params.interface)


class InterfaceListTestCase(Check):
    def __init__(self, **kwargs):
        super().__init__(
            check_type="interface-list",
            check_params=BaseModel(),
            expected_results=BaseModel(),
            **kwargs
        )

    def check_id(self) -> str:
        return "exclusive_list"


@design_checks
class InterfaceTestCases(CheckCollection):
    service = "interfaces"
    checks: Optional[List[InterfaceTestCase]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> "InterfaceTestCases":
        def build_test_case(iface: DeviceInterface):

            # if the interface is not used, meaning it is not part of the
            # design, then there is no profile, and .enabled=False.  No other
            # interface valiation is required for operational state.

            if not iface.used:
                expected_results = InterfaceTestNotUsedExpectations(used=False)
                if_flags = None

            # if the interface is used (in design) it still could be shutdown
            # (.enabled=False). we would still want to check the reporting speed
            # and descriptions as defined.

            else:
                port_profile = iface.profile.port_profile
                if_flags = iface.profile.profile_flags

                expected_results = InterfaceTestUsedExpectations(
                    used=True,
                    desc=iface.desc,
                    oper_up=iface.enabled,
                    speed=port_profile.speed if port_profile else None,
                )

                if iface.profile.is_reserved:
                    expected_results.oper_up = None

            return InterfaceTestCase(
                check_params=InterfaceTestParams(
                    interface=iface.name, interface_flags=if_flags
                ),
                expected_results=expected_results,
            )

        test_cases = InterfaceTestCases(
            device=device.name,
            checks=[
                build_test_case(iface=interface)
                for if_name, interface in device.interfaces.items()
            ],
        )

        # return the test cases sorted by the lag interface name
        test_cases.checks.sort(
            key=lambda tc: DeviceInterface(tc.check_params.interface)
        )
        return test_cases
