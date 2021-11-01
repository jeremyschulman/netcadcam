# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Dict, Optional

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.test_services import TestCases, TestCase
from netcad.test_services import testing_service


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
    port_type: Optional[str]
    desc: str


def _interfaces_as_dict(device: Device) -> dict:
    as_dict = dict()

    for if_name, iface in device.interfaces.iter_used().items():
        port_type = (
            iface.profile.port_profile.name if iface.profile.port_profile else None
        )

        as_dict[if_name] = DeviceInterfaceInfo(
            name=if_name, enabled=iface.enabled, desc=iface.desc, port_type=port_type
        )

    return as_dict


@testing_service
class DeviceInformationTestCases(TestCases):
    service = "device"
    tests: List[DeviceInformationTestCase]
    interfaces: Dict[str, DeviceInterfaceInfo]

    @classmethod
    def build(cls, device: Device) -> "DeviceInformationTestCases":

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
