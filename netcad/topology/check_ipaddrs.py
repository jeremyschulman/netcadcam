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
from netcad.checks import CheckCollection, Check
from netcad.checks import design_checks

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "IpInterfacesCheckCollection",
    "IpInterfaceCheck",
    "IpInterfaceCheckExclusiveList",
]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class IpInterfaceCheckParams(BaseModel):
    if_name: str


class IpInterfaceCheckExpectations(BaseModel):
    if_ipaddr: str


class IpInterfaceCheck(Check):
    check_params: IpInterfaceCheckParams
    expected_results: IpInterfaceCheckExpectations

    def check_id(self) -> str:
        return str(self.check_params.if_name)


class IpInterfaceCheckExclusiveList(Check):
    def __init__(self, **kwargs):
        super().__init__(
            check_type="ipaddrs-list",
            check_params=BaseModel(),
            expected_results=BaseModel(),
            **kwargs
        )

    def check_id(self) -> str:
        return "exclusive_list"


@design_checks
class IpInterfacesCheckCollection(CheckCollection):
    service = "ipaddrs"
    checks: Optional[List[IpInterfaceCheck]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> Optional["IpInterfacesCheckCollection"]:
        if_l3_list = [
            iface
            for iface in device.interfaces.used().values()
            if isinstance(iface.profile, InterfaceL3)
            and (iface.profile.if_ipaddr or iface.profile.is_reserved)
        ]

        return IpInterfacesCheckCollection(
            device=device.name,
            checks=[
                IpInterfaceCheck(
                    check_params=IpInterfaceCheckParams(if_name=iface.name),
                    expected_results=IpInterfaceCheckExpectations(
                        if_ipaddr=str(iface.profile.if_ipaddr or "is_reserved")
                    ),
                )
                for iface in if_l3_list
            ],
        )
