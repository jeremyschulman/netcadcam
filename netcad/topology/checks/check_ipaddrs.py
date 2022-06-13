#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

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
from netcad.device.profiles.l3_interfaces import InterfaceL3
from netcad.checks import CheckCollection, Check
from netcad.checks import register_collection

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "IPInterfacesCheckCollection",
    "IPInterfaceCheck",
    "IPInterfaceCheckExclusiveList",
    "IPInterfaceList",
]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class IPInterfaceCheckParams(BaseModel):
    if_name: str


class IPInterfaceCheckExpectations(BaseModel):
    if_ipaddr: str
    # TODO: add enabled state, for when the IP is not expected to be "up"


class IPInterfaceCheck(Check):
    check_params: IPInterfaceCheckParams
    expected_results: IPInterfaceCheckExpectations

    def check_id(self) -> str:
        return str(self.check_params.if_name)


class IPInterfaceList(BaseModel):
    if_names: List[str]


class IPInterfaceCheckExclusiveList(Check):
    expected_results: IPInterfaceList

    def check_id(self) -> str:
        return "exclusive_list"


@register_collection
class IPInterfacesCheckCollection(CheckCollection):
    name = "ipaddrs"
    checks: Optional[List[IPInterfaceCheck]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> Optional["IPInterfacesCheckCollection"]:
        if_l3_list = [
            iface
            for iface in device.interfaces.used().values()
            if isinstance(iface.profile, InterfaceL3)
            and (iface.profile.if_ipaddr or iface.profile.is_reserved)
        ]

        return IPInterfacesCheckCollection(
            device=device.name,
            exclusive=not device.is_not_exclusive,
            checks=[
                IPInterfaceCheck(
                    check_params=IPInterfaceCheckParams(if_name=iface.name),
                    expected_results=IPInterfaceCheckExpectations(
                        if_ipaddr=str(iface.profile.if_ipaddr or "is_reserved")
                    ),
                )
                for iface in if_l3_list
            ],
        )
