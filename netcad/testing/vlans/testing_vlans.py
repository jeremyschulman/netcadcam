# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List


# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.testing import TestCases, TestCase
from netcad.vlan import VlanProfile

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "build_vlan_tests",
    "VlanTestCase",
    "VlanTestParams",
    "VlanTestExpectations",
    "VlanTestCases",
]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class VlanTestParams(BaseModel):
    vlan_id: int


class VlanTestExpectations(BaseModel):
    vlan: VlanProfile
    interfaces: List[str]


class VlanTestCase(TestCase):
    test_params: VlanTestParams
    expected_results: VlanTestExpectations

    def test_case_id(self) -> str:
        return str(self.test_params.vlan_id)


class VlanTestCases(TestCases):
    tests: List[VlanTestCase]


def build_vlan_tests(device: Device) -> VlanTestCases:

    vlans = device.vlans()

    test_cases = TestCases(service="vlans")
    test_cases.tests.extend(
        [
            TestCase(
                test_case="vlan-exists",
                device=device.name,
                test_params=VlanTestParams(vlan_id=each_vlan.vlan_id),
                expected_results=VlanTestExpectations(
                    vlan=each_vlan, interfaces=["one", "two"]
                ),
            )
            for each_vlan in vlans
        ]
    )

    return test_cases
