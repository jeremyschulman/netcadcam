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
from netcad.testing_services import TestCases, TestCase
from netcad.testing_services import testing_service


class DeviceInformationTestParams(BaseModel):
    device: str
    os_name: str


class DeviceInformationTestExpectations(BaseModel):
    product_model: str


class DeviceInformationTestCase(TestCase):
    test_params: DeviceInformationTestParams
    expected_results: DeviceInformationTestExpectations

    def test_case_id(self) -> str:
        return self.test_params.device


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


@testing_service
class DeviceInformationTestCases(TestCases):
    service = "device"
    tests: List[DeviceInformationTestCase]
    interfaces: Dict[str, DeviceInterfaceInfo]

    @classmethod
    def build(cls, device: Device, **kwargs) -> "DeviceInformationTestCases":

        return DeviceInformationTestCases(
            device=device.name,
            interfaces=_interfaces_as_dict(device),
            tests=[
                DeviceInformationTestCase(
                    test_params=DeviceInformationTestParams(
                        device=device.name, os_name=device.os_name
                    ),
                    expected_results=DeviceInformationTestExpectations(
                        product_model=device.product_model
                    ),
                )
            ],
        )
