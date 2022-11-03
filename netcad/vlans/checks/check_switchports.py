#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional, Union

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, validator

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.vlans import VlanProfile
from netcad.vlans.profiles.l2_interfaces import InterfaceL2Access, InterfaceL2Trunk

from netcad.checks import (
    CheckCollection,
    Check,
    CheckResult,
    CheckMeasurement,
    register_collection,
)


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["SwitchportCheckCollection", "SwitchportCheck", "SwitchportCheckResult"]


# -----------------------------------------------------------------------------
# Check interface switchport status
# -----------------------------------------------------------------------------


class SwitchportCheck(Check):
    check_type = "switchport"

    class Params(BaseModel):
        if_name: str

    class ExpectSwitchport(BaseModel):
        switchport_mode: Optional[str]

    class ExpectAccess(ExpectSwitchport):
        switchport_mode = "access"
        vlan: VlanProfile

    class ExpectTrunk(ExpectSwitchport):
        switchport_mode = "trunk"
        native_vlan: Optional[VlanProfile]
        trunk_allowed_vlans: List[VlanProfile]

    check_params: Params
    expected_results: Union[ExpectAccess, ExpectTrunk]

    def check_id(self) -> str:
        return str(self.check_params.if_name)


class SwitchportCheckResult(CheckResult[SwitchportCheck]):
    """
    This one is a bit tricky due to the name of the access | trunk. We declare
    the measuretype to be the generalized form first.  Then depending on the
    value we will be more specific:

    """

    class Measurement(CheckMeasurement, SwitchportCheck.ExpectSwitchport):
        pass

    class MeasuredAccess(CheckMeasurement, SwitchportCheck.ExpectAccess):
        pass

    class MeasuredTrunk(CheckMeasurement, SwitchportCheck.ExpectTrunk):
        pass

    measurement: Measurement = None

    @validator("measurement", pre=True, always=True)
    def _on_measurement(cls, value, values):
        check = values["check"]
        msrd_type = (
            SwitchportCheckResult.MeasuredAccess
            if check.expected_results.switchport_mode == "access"
            else SwitchportCheckResult.MeasuredTrunk
        )
        return msrd_type.parse_obj({})


# -----------------------------------------------------------------------------


@register_collection
class SwitchportCheckCollection(CheckCollection):
    name = "switchports"
    checks: Optional[List[SwitchportCheck]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> "SwitchportCheckCollection":

        checks = list()

        for if_name, interface in device.interfaces.used().items():
            if_prof = interface.profile
            tc_params = SwitchportCheck.Params(if_name=if_name)

            if isinstance(if_prof, InterfaceL2Access):
                tc_expd = SwitchportCheck.ExpectAccess(vlan=if_prof.vlan)

            elif isinstance(if_prof, InterfaceL2Trunk):
                # there are cases where a trunk port does not have a native
                # VLAN defined.  In those cases the native_vlan attribute will
                # not exist in the interface profile.

                native_vlan = getattr(if_prof, 'native_vlan', None)

                tc_expd = SwitchportCheck.ExpectTrunk(
                    native_vlan=native_vlan,
                    trunk_allowed_vlans=sorted(if_prof.trunk_allowed_vlans()),
                )
            else:
                continue

            checks.append(
                SwitchportCheck(check_params=tc_params, expected_results=tc_expd)
            )

        return SwitchportCheckCollection(device=device.name, checks=checks)
