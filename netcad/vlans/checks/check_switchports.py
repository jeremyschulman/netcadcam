#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

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
from netcad.vlans import VlanProfile
from netcad.vlans.profiles.l2_interfaces import InterfaceL2Access, InterfaceL2Trunk

from netcad.checks import CheckCollection, Check
from netcad.checks.check_registry import register_collection


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "SwitchportCheckCollection",
    "SwitchportCheck",
    "SwitchportTrunkExpectation",
    "SwitchportAccessExpectation",
]


class SwitchportCheckParams(BaseModel):
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


class SwitchportCheck(Check):
    check_type = "switchport"
    check_params: SwitchportCheckParams
    expected_results: SwitchportExpectations

    def check_id(self) -> str:
        return str(self.check_params.if_name)


@register_collection
class SwitchportCheckCollection(CheckCollection):
    name = "switchports"
    checks: Optional[List[SwitchportCheck]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> "SwitchportCheckCollection":

        checks = list()

        for if_name, interface in device.interfaces.used().items():
            if_prof = interface.profile
            tc_params = SwitchportCheckParams(if_name=if_name)

            if isinstance(if_prof, InterfaceL2Access):
                tc_expd = SwitchportAccessExpectation(vlan=if_prof.vlan)

            elif isinstance(if_prof, InterfaceL2Trunk):
                tc_expd = SwitchportTrunkExpectation(
                    native_vlan=if_prof.native_vlan,
                    trunk_allowed_vlans=sorted(if_prof.trunk_allowed_vlans()),
                )
            else:
                continue

            checks.append(
                SwitchportCheck(check_params=tc_params, expected_results=tc_expd)
            )

        return SwitchportCheckCollection(device=device.name, checks=checks)
