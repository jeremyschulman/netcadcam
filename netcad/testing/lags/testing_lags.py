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
from netcad.testing import TestCases, TestCase
from netcad.device import InterfaceLag

from netcad.testing import testing_service

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["LagTestCases", "LagTestCase", "LagTestParams", "LagTestExpectations"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class LagTestParams(BaseModel):
    if_name: str


class LagTestExpectations(BaseModel):
    status: str  # TODO: should make this an Enum
    interfaces: List[str]


class LagTestCase(TestCase):
    test_params: LagTestParams
    expected_results: LagTestExpectations

    def test_case_id(self) -> str:
        return str(self.test_params.if_name)


@testing_service
class LagTestCases(TestCases):
    service = "lags"
    tests: Optional[List[LagTestCase]]

    @classmethod
    def build(cls, device: Device) -> "LagTestCases":

        lag_interfaces = defaultdict(list)

        for if_name, interface in device.interfaces.iter_used():
            if not isinstance(interface.profile, InterfaceLag):
                continue

            if_lag = interface.profile.lag_parent
            lag_interfaces[if_lag.name].extend(
                iface.name for iface in interface.profile.if_lag_members
            )

        test_cases = LagTestCases(
            tests=[
                LagTestCase(
                    test_case="lag",
                    device=device.name,
                    test_params=LagTestParams(if_name=lag_name),
                    expected_results=LagTestExpectations(
                        # TODO: REMOVE hardcoded "bunded" status.  Set the
                        #       expected status from the design?
                        status="bundled",
                        interfaces=if_names,
                    ),
                )
                for lag_name, if_names in lag_interfaces.items()
            ]
        )

        # return the test cases sorted by the lag interface name
        test_cases.tests.sort(key=lambda tc: DeviceInterface(tc.test_params.if_name))
        return test_cases
