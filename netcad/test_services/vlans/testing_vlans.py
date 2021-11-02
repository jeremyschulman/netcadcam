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

from netcad.device import Device
from netcad.test_services import TestCases, TestCase
from netcad.vlan import VlanProfile
from netcad.test_services.testing_registry import testing_service

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
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


# -----------------------------------------------------------------------------
#
#
# -----------------------------------------------------------------------------


@testing_service
class VlanTestCases(TestCases):
    service = "vlans"
    tests: Optional[List[VlanTestCase]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> "VlanTestCases":

        vlan_interfaces = defaultdict(list)

        for if_name, interface in device.interfaces.items():
            if not interface.profile:
                continue

            if not (vlans_used := getattr(interface.profile, "vlans_used", None)):
                continue

            for vlan in vlans_used():
                vlan_interfaces[vlan].append(if_name)

        test_cases = VlanTestCases(
            device=device.name,
            tests=[
                VlanTestCase(
                    test_case="vlan-exists",
                    test_params=VlanTestParams(vlan_id=vlan_p.vlan_id),
                    expected_results=VlanTestExpectations(
                        vlan=vlan_p, interfaces=if_names
                    ),
                )
                for vlan_p, if_names in vlan_interfaces.items()
            ],
        )

        # return the test-cases sorted by VLAN-ID
        test_cases.tests.sort(key=lambda tc: tc.test_params.vlan_id)
        return test_cases
