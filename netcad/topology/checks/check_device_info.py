#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Dict, Optional, ClassVar

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
    Check,
    CheckResult,
    CheckMeasurement,
)


from ..topology_feature import TopologyDesignFeature

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


class DeviceInformationCheckExpect(BaseModel):
    product_model: str


class DeviceInformationCheck(Check):
    check_type: str = "device-info"

    class Params(BaseModel):
        device: str
        os_name: str

    Expect = DeviceInformationCheckExpect
    check_params: Params
    expected_results: DeviceInformationCheckExpect

    def check_id(self) -> str:
        return self.check_params.device


class DeviceInformationCheckResult(CheckResult[DeviceInformationCheck]):
    class Measurement(DeviceInformationCheck.Expect, CheckMeasurement):
        pass

    measurement: Measurement


class DeviceInterfaceInfo(BaseModel):
    name: str
    enabled: bool
    used: bool
    port_type: Optional[str] = Field("")
    desc: Optional[str] = Field("")
    profile_flags: Optional[dict] = Field(default_factory=dict)


def _interfaces_as_dict(device: Device) -> dict:
    as_dict = dict()

    for iface in sorted(device.interfaces.values()):
        iface = device.interfaces[iface.name]
        if not iface.used:
            as_dict[iface.name] = DeviceInterfaceInfo(
                used=False, name=iface.name, enabled=iface.enabled, desc=iface.desc
            )
            continue

        if_prof = iface.profile

        # extract the physical port type name from the profile, if it exists;
        # otherwise it is set to None.  It should never be None, FWIW.
        # TODO: perhaps log error?

        port_type = None if not (ifphy_prof := if_prof.phy_profile) else ifphy_prof.name

        flags = if_prof.profile_flags

        as_dict[iface.name] = DeviceInterfaceInfo(
            used=True,
            name=iface.name,
            enabled=iface.enabled,
            desc=iface.desc,
            port_type=port_type,
            profile_flags=flags,
        )

    return as_dict


@TopologyDesignFeature.register_check_collection
class DeviceInformationCheckCollection(CheckCollection):
    name: ClassVar[str] = "device"
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
