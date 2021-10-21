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
from netcad.testing import TestCases, TestCase
from netcad.vlan import VlanProfile

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


class VlanTestCases(TestCases):
    service = "vlans"
    tests: Optional[List[VlanTestCase]]

    @classmethod
    def build(cls, device: Device) -> "VlanTestCases":

        # vlans = device.vlans()
        vlan_interfaces = defaultdict(list)

        for if_name, interface in device.interfaces.items():
            if not interface.profile:
                continue

            if not (vlans_used := getattr(interface.profile, "vlans_used", None)):
                continue

            for vlan in vlans_used():
                vlan_interfaces[vlan].append(if_name)

        test_cases = VlanTestCases(
            tests=[
                VlanTestCase(
                    test_case="vlan-exists",
                    device=device.name,
                    test_params=VlanTestParams(vlan_id=vlan_p.vlan_id),
                    expected_results=VlanTestExpectations(
                        vlan=vlan_p, interfaces=if_names
                    ),
                )
                for vlan_p, if_names in vlan_interfaces.items()
            ]
        )

        return test_cases
