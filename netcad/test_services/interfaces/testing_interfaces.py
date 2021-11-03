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
from netcad.test_services import TestCases, TestCase
from netcad.test_services import testing_service

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = []

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class InterfaceTestParams(BaseModel):
    interface: str


class InterfaceTestUsedExpectations(BaseModel):
    used: Literal[True]
    oper_up: bool
    desc: str
    speed: Optional[PositiveInt]


class InterfaceTestNotUsedExpectations(BaseModel):
    used: Literal[False]


class InterfaceTestCase(TestCase):
    test_params: InterfaceTestParams
    expected_results: Union[
        InterfaceTestUsedExpectations, InterfaceTestNotUsedExpectations
    ]

    def test_case_id(self) -> str:
        return str(self.test_params.interface)


@testing_service
class InterfaceTestCases(TestCases):
    service = "interfaces"
    tests: Optional[List[InterfaceTestCase]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> "InterfaceTestCases":
        def build_test_case(iface: DeviceInterface):

            # if the interface is not used, meaning it is not part of the
            # design, then there is no profile, and .enabled=False.  No other
            # interface valiation is required for operational state.

            if not iface.used:
                expected_results = InterfaceTestNotUsedExpectations(used=False)

            # if the interface is used (in design) it still could be shutdown
            # (.enabled=False). we would still want to check the reporting speed
            # and descriptions as defined.

            else:
                port_profile = iface.profile.port_profile
                expected_results = InterfaceTestUsedExpectations(
                    used=True,
                    desc=iface.desc,
                    oper_up=iface.enabled,
                    speed=port_profile.speed if port_profile else None,
                )

            return InterfaceTestCase(
                test_params=InterfaceTestParams(interface=iface.name),
                expected_results=expected_results,
            )

        test_cases = InterfaceTestCases(
            device=device.name,
            tests=[
                build_test_case(iface=interface)
                for if_name, interface in device.interfaces.items()
            ],
        )

        # return the test cases sorted by the lag interface name
        test_cases.tests.sort(key=lambda tc: DeviceInterface(tc.test_params.interface))
        return test_cases
