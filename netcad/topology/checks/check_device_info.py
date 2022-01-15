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
from netcad.checks import CheckCollection, Check, register_collection


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class DeviceInformationCheckParams(BaseModel):
    device: str
    os_name: str


class DeviceInformationCheckExpectations(BaseModel):
    product_model: str


class DeviceInformationCheck(Check):
    check_params: DeviceInformationCheckParams
    expected_results: DeviceInformationCheckExpectations

    def check_id(self) -> str:
        return self.check_params.device


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

        port_type = (
            None if not (ifphy_prof := if_prof.port_profile) else ifphy_prof.name
        )

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
                    check_params=DeviceInformationCheckParams(
                        device=device.name, os_name=device.os_name
                    ),
                    expected_results=DeviceInformationCheckExpectations(
                        product_model=device.product_model
                    ),
                )
            ],
        )
