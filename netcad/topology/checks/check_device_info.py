#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Dict, Optional

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, Field

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.checks import (
    CheckCollection,
    register_collection,
    Check,
    CheckResult,
    CheckMeasurement,
)


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "DeviceInformationCheckCollection",
    "DeviceInformationCheck",
    "DeviceInformationCheckResult",
]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class DeviceInformationCheck(Check):
    check_type = "device-info"

    class Params(BaseModel):
        device: str
        os_name: str

    class Expect(BaseModel):
        product_model: str

    check_params: Params
    expected_results: Expect

    def check_id(self) -> str:
        return self.check_params.device


class DeviceInformationCheckResult(CheckResult[DeviceInformationCheck]):
    class Measurement(DeviceInformationCheck.Expect, CheckMeasurement):
        pass

    measurement: Measurement = None


class DeviceInterfaceInfo(BaseModel):
    name: str
    enabled: bool
    used: bool
    port_type: Optional[str]
    desc: Optional[str] = Field("")
    profile_flags: Optional[dict] = Field(default_factory=dict)


def _interfaces_as_dict(device: Device) -> dict:
    as_dict = dict()

    for if_name, iface in device.interfaces.items():
        if not iface.used:
            as_dict[if_name] = DeviceInterfaceInfo(
                used=False, name=if_name, enabled=iface.enabled, desc=iface.desc
            )
            continue

        if_prof = iface.profile

        # extract the physical port type name from the profile, if it exists;
        # otherwise it is set to None.  It should never be None, FWIW.
        # TODO: perhaps log error?

        port_type = None if not (ifphy_prof := if_prof.phy_profile) else ifphy_prof.name

        flags = if_prof.profile_flags

        as_dict[if_name] = DeviceInterfaceInfo(
            used=True,
            name=if_name,
            enabled=iface.enabled,
            desc=iface.desc,
            port_type=port_type,
            profile_flags=flags,
        )

    return as_dict


@register_collection
class DeviceInformationCheckCollection(CheckCollection):
    name = "device"
    checks: List[DeviceInformationCheck]
    interfaces: Dict[str, DeviceInterfaceInfo]

    @classmethod
    def build(cls, device: Device, **kwargs) -> "DeviceInformationCheckCollection":
        return DeviceInformationCheckCollection(
            device=device.name,
            interfaces=_interfaces_as_dict(device),
            checks=[
                DeviceInformationCheck(
                    check_params=DeviceInformationCheck.Params(
                        device=device.name, os_name=device.os_name
                    ),
                    expected_results=DeviceInformationCheck.Expect(
                        product_model=device.product_model
                    ),
                )
            ],
        )
