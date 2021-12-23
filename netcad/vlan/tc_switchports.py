# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional, Union

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.vlan import VlanProfile
from netcad.device.l2_interfaces import InterfaceL2Access, InterfaceL2Trunk

from netcad.checks import CheckCollection, Check
from netcad.checks.check_registry import design_checks


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "SwitchportTestCases",
    "SwitchportTestCase",
    "SwitchportTrunkExpectation",
    "SwitchportAccessExpectation",
]


class SwitchportTestParams(BaseModel):
    if_name: str


class SwitchportAnyExpectations(BaseModel):
    switchport_mode: str


class SwitchportAccessExpectation(SwitchportAnyExpectations):
    switchport_mode = "access"
    vlan: VlanProfile


class SwitchportTrunkExpectation(SwitchportAnyExpectations):
    switchport_mode = "trunk"
    native_vlan: Optional[VlanProfile]
    trunk_allowed_vlans: List[VlanProfile]


SwitchportExpectations = Union[SwitchportAccessExpectation, SwitchportTrunkExpectation]


class SwitchportTestCase(Check):
    check_type = "switchport"
    check_params: SwitchportTestParams
    expected_results: SwitchportExpectations

    def check_id(self) -> str:
        return str(self.check_params.if_name)


@design_checks
class SwitchportTestCases(CheckCollection):
    service = "switchports"
    checks: Optional[List[SwitchportTestCase]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> "SwitchportTestCases":

        test_cases = list()

        for if_name, interface in device.interfaces.used().items():
            if_prof = interface.profile
            tc_params = SwitchportTestParams(if_name=if_name)

            if isinstance(if_prof, InterfaceL2Access):
                tc_expd = SwitchportAccessExpectation(vlan=if_prof.vlan)

            elif isinstance(if_prof, InterfaceL2Trunk):
                tc_expd = SwitchportTrunkExpectation(
                    native_vlan=if_prof.native_vlan,
                    trunk_allowed_vlans=sorted(if_prof.trunk_allowed_vlans()),
                )
            else:
                continue

            test_cases.append(
                SwitchportTestCase(check_params=tc_params, expected_results=tc_expd)
            )

        return SwitchportTestCases(device=device.name, checks=test_cases)
