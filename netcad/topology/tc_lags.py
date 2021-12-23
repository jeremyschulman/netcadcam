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
from netcad.checks import CheckCollection, Check
from netcad.device import InterfaceLag

from netcad.checks import design_checks

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


class LagTestCase(Check):
    check_params: LagTestParams
    expected_results: LagTestExpectations

    def check_id(self) -> str:
        return str(self.check_params.interface)


@design_checks
class LagTestCases(CheckCollection):
    service = "lags"
    checks: Optional[List[LagTestCase]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> Optional["LagTestCases"]:

        # scan the device interfaces looking for LAGs.  Create a dictionary
        # key=lag-if-name, value=list of member interfaces.

        lag_interfaces = defaultdict(list)

        for if_name, interface in device.interfaces.used().items():
            if not isinstance(interface.profile, InterfaceLag):
                continue

            # TODO: not sure why this is here now; should
            #       just be using interface
            # if_lag = interface.profile.lag_parent
            # if not if_lag:
            #     breakpoint()
            #     x=1

            lag_interfaces[interface.name].extend(
                iface for iface in interface.profile.if_lag_members
            )

        # if no lags found, then return None so that the test cases file
        # is not generated.

        if not lag_interfaces:
            return None

        # create the list of test-cases using the formulated dictionary.

        test_cases = LagTestCases(
            device=device.name,
            checks=[
                LagTestCase(
                    check_type="lag",
                    check_params=LagTestParams(interface=lag_name),
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
        test_cases.checks.sort(
            key=lambda tc: DeviceInterface(tc.check_params.interface)
        )
        return test_cases
