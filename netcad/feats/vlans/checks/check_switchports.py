#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional, Union, ClassVar, Any, Literal

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, Field

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from .. import VlanProfile
from ..profiles.l2_interfaces import InterfaceL2Access, InterfaceL2Trunk

from ..vlan_feat import VlansDesignFeature


from netcad.checks import (
    CheckCollection,
    Check,
    CheckResult,
    CheckMeasurement,
)


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "SwitchportCheckCollection",
    "SwitchportCheck",
    "SwitchportCheckResult",
    "MeasurementSwitchPort",
    "MeasurementSwitchPortAccess",
    "MeasurementSwitchPortTrunk",
]


# -----------------------------------------------------------------------------
# Check interface switchport status
# -----------------------------------------------------------------------------


class SwitchportCheck(Check):
    check_type: str = "switchport"

    class Params(BaseModel):
        if_name: str

    class ExpectSwitchport(BaseModel):
        switchport_mode: str

    class ExpectAccess(ExpectSwitchport):
        switchport_mode: Literal["access"] = Field("access")
        vlan: VlanProfile | int

    class ExpectTrunk(ExpectSwitchport):
        switchport_mode: Literal["trunk"] = Field("trunk")
        native_vlan: Optional[VlanProfile | int]
        trunk_allowed_vlans: List[VlanProfile | int] | str

    check_params: Params
    expected_results: Union[ExpectAccess, ExpectTrunk] = Field(
        ..., discriminator="switchport_mode"
    )

    def check_id(self) -> str:
        return str(self.check_params.if_name)


class MeasurementSwitchPort(CheckMeasurement, SwitchportCheck.ExpectSwitchport):
    switchport_mode: str = Field(..., description="The switchport mode")


class MeasurementSwitchPortAccess(MeasurementSwitchPort):
    switchport_mode: str = Field("access")
    vlan: int


class MeasurementSwitchPortTrunk(MeasurementSwitchPort):
    switchport_mode: str = Field("trunk")
    native_vlan: Optional[int]
    trunk_allowed_vlans: str


class SwitchportCheckResult(CheckResult[SwitchportCheck]):
    """
    This one is a bit tricky due to the name of the access | trunk. We declare
    the measuretype to be the generalized form first.  Then depending on the
    value we will be more specific:

    """

    measurement: Union[
        MeasurementSwitchPortAccess, MeasurementSwitchPortTrunk | None
    ] = Field(..., discriminator="switchport_mode")

    # @field_validator("measurement", mode="after")
    # @classmethod
    # def _on_measurement(cls, value):
    #     breakpoint()
    #     check = value
    #     msrd_type = (
    #         MeasurementSwitchPortAccess
    #         if check.expected_results.switchport_mode == "access"
    #         else MeasurementSwitchPortTrunk
    #     )
    #     return msrd_type.model_validate({})


# -----------------------------------------------------------------------------


@VlansDesignFeature.register_check_collection
class SwitchportCheckCollection(CheckCollection):
    name: ClassVar[str] = "switchports"
    checks: Optional[List[SwitchportCheck]]
    config: Optional[Any]

    @classmethod
    def build(
        cls, device: Device, design_feature: "VlansDesignFeature"
    ) -> "SwitchportCheckCollection":
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

                native_vlan = getattr(if_prof, "native_vlan", None)

                tc_expd = SwitchportCheck.ExpectTrunk(
                    native_vlan=native_vlan,
                    trunk_allowed_vlans=sorted(if_prof.trunk_allowed_vlans()),
                )
            else:
                continue

            checks.append(
                SwitchportCheck(check_params=tc_params, expected_results=tc_expd)
            )

        return SwitchportCheckCollection(
            device=device.name, checks=checks, config=design_feature.config
        )
