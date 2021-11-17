# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional
from collections import defaultdict

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device, DeviceInterface
from netcad.testing_services import TestCases, TestCase
from netcad.device import InterfaceLag

from netcad.testing_services import testing_service

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "LagTestCases",
    "LagTestCase",
    "LagTestParams",
    "LagTestExpectations",
    "LagTestExpectedInterfaceStatus",
]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class LagTestParams(BaseModel):
    interface: str


class LagTestExpectedInterfaceStatus(BaseModel):
    interface: str
    enabled: bool


class LagTestExpectations(BaseModel):
    enabled: bool
    interfaces: List[LagTestExpectedInterfaceStatus]


class LagTestCase(TestCase):
    test_params: LagTestParams
    expected_results: LagTestExpectations

    def test_case_id(self) -> str:
        return str(self.test_params.interface)


@testing_service
class LagTestCases(TestCases):
    service = "lags"
    tests: Optional[List[LagTestCase]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> Optional["LagTestCases"]:

        # scan the device interfaces looking for LAGs.  Create a dictionary
        # key=lag-if-name, value=list of member interfaces.

        lag_interfaces = defaultdict(list)

        for if_name, interface in device.interfaces.used().items():
            if not isinstance(interface.profile, InterfaceLag):
                continue

            if_lag = interface.profile.lag_parent
            lag_interfaces[if_lag.name].extend(
                iface for iface in interface.profile.if_lag_members
            )

        # if no lags found, then return None so that the test cases file
        # is not generated.

        if not lag_interfaces:
            return None

        # create the list of test-cases using the formulated dictionary.

        test_cases = LagTestCases(
            device=device.name,
            tests=[
                LagTestCase(
                    test_case="lag",
                    test_params=LagTestParams(interface=lag_name),
                    expected_results=LagTestExpectations(
                        enabled=device.interfaces[lag_name].enabled,
                        interfaces=[
                            LagTestExpectedInterfaceStatus(
                                interface=each_interface.name,
                                enabled=each_interface.enabled,
                            )
                            for each_interface in lag_interfaces
                        ],
                    ),
                )
                for lag_name, lag_interfaces in lag_interfaces.items()
            ],
        )

        # return the test cases sorted by the lag interface name
        test_cases.tests.sort(key=lambda tc: DeviceInterface(tc.test_params.interface))
        return test_cases
