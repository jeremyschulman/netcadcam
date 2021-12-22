# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.device.l3_interfaces import InterfaceL3
from netcad.testing_services import TestCases, TestCase
from netcad.testing_services import testing_service

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "IPInterfacesTestCases",
    "IPInterfaceTestCase",
    "IPInterfaceExclusiveListTestCase",
]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class IPInterfaceTestParams(BaseModel):
    if_name: str


class IPInterfaceTestExpectations(BaseModel):
    if_ipaddr: str


class IPInterfaceTestCase(TestCase):
    test_params: IPInterfaceTestParams
    expected_results: IPInterfaceTestExpectations

    def test_case_id(self) -> str:
        return str(self.test_params.if_name)


class IPInterfaceExclusiveListTestCase(TestCase):
    def __init__(self, **kwargs):
        super().__init__(
            test_case="ipaddrs-list",
            test_params=BaseModel(),
            expected_results=BaseModel(),
            **kwargs
        )

    def test_case_id(self) -> str:
        return "exclusive_list"


@testing_service
class IPInterfacesTestCases(TestCases):
    service = "ipaddrs"
    tests: Optional[List[IPInterfaceTestCase]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> Optional["IPInterfacesTestCases"]:
        if_l3_list = [
            iface
            for iface in device.interfaces.used().values()
            if isinstance(iface.profile, InterfaceL3)
            and (iface.profile.if_ipaddr or iface.profile.is_reserved)
        ]

        return IPInterfacesTestCases(
            device=device.name,
            tests=[
                IPInterfaceTestCase(
                    test_params=IPInterfaceTestParams(if_name=iface.name),
                    expected_results=IPInterfaceTestExpectations(
                        if_ipaddr=str(iface.profile.if_ipaddr or "is_reserved")
                    ),
                )
                for iface in if_l3_list
            ],
        )
