#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional, ClassVar

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.device.profiles.l3_interfaces import InterfaceL3
from netcad.checks import CheckCollection, Check, CheckResult, CheckMeasurement
from netcad.checks import CheckExclusiveList, CheckExclusiveResult
from ..topology_feature import TopologyDesignFeature

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "IPInterfacesCheckCollection",
    "IPInterfaceCheck",
    "IPInterfaceCheckResult",
    "IPInterfaceExclusiveListCheck",
    "IPInterfaceExclusiveListCheckResult",
]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class IPInterfaceCheckExpect(BaseModel):
    if_ipaddr: str
    # TODO: for now this check hardcoded the expectation that the interface
    #       bound to this IP address is in the "up" condition.  In the
    #       future we could make this configurable based on the design.
    oper_up: bool = True


class IPInterfaceCheck(Check):
    check_type: str = "ipaddr"

    class Params(BaseModel):
        if_name: str

    class Expect(IPInterfaceCheckExpect):
        pass

    check_params: Params
    expected_results: IPInterfaceCheckExpect

    def check_id(self) -> str:
        return str(self.check_params.if_name)


class IPInterfaceCheckResult(CheckResult[IPInterfaceCheck]):
    class Measurement(IPInterfaceCheck.Expect, CheckMeasurement):
        pass

    measurement: Measurement = None


# -----------------------------------------------------------------------------
# Check for exclusive list of IP interfaces
# -----------------------------------------------------------------------------


class IPInterfaceExclusiveListCheck(Check):
    check_type: str = "ipaddrs-exclusive"

    expected_results: CheckExclusiveList


class IPInterfaceExclusiveListCheckResult(
    CheckExclusiveResult[IPInterfaceExclusiveListCheck]
):
    class Measurement(CheckExclusiveList, CheckMeasurement):
        pass

    measurement: Measurement = None


# -----------------------------------------------------------------------------


@TopologyDesignFeature.register_check_collection
class IPInterfacesCheckCollection(CheckCollection):
    name: ClassVar[str] = "ipaddrs"
    checks: Optional[List[IPInterfaceCheck]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> Optional["IPInterfacesCheckCollection"]:
        if_l3_list = [
            iface
            for iface in sorted(device.interfaces.used().values())
            if isinstance(iface.profile, InterfaceL3)
            and (iface.profile.if_ipaddr or iface.profile.is_reserved)
        ]

        return IPInterfacesCheckCollection(
            device=device.name,
            exclusive=not device.is_not_exclusive,
            checks=[
                IPInterfaceCheck(
                    check_params=IPInterfaceCheck.Params(if_name=iface.name),
                    expected_results=IPInterfaceCheck.Expect(
                        if_ipaddr=str(iface.profile.if_ipaddr or "is_reserved")
                    ),
                )
                for iface in if_l3_list
            ],
        )
