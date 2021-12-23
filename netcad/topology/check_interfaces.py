# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional, Union, Literal

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, PositiveInt

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device, DeviceInterface
from netcad.checks import CheckCollection, Check
from netcad.checks import design_checks

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "InterfaceCheckCollection",
    "InterfaceCheck",
    "InterfaceCheckParams",
    "InterfaceCheckUsedExpectations",
    "InterfaceCheckNotUsedExpectations",
    "InterfaceCheckExclusiveList",
]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class InterfaceCheckParams(BaseModel):
    interface: str
    interface_flags: Optional[dict]


class InterfaceCheckUsedExpectations(BaseModel):
    used: Literal[True]
    oper_up: Optional[bool]
    desc: str
    speed: Optional[PositiveInt]


class InterfaceCheckNotUsedExpectations(BaseModel):
    used: Literal[False]


class InterfaceCheck(Check):
    check_params: InterfaceCheckParams
    expected_results: Union[
        InterfaceCheckUsedExpectations, InterfaceCheckNotUsedExpectations
    ]

    def check_id(self) -> str:
        return str(self.check_params.interface)


class InterfaceCheckExclusiveList(Check):
    def __init__(self, **kwargs):
        super().__init__(
            check_type="interface-list",
            check_params=BaseModel(),
            expected_results=BaseModel(),
            **kwargs
        )

    def check_id(self) -> str:
        return "exclusive_list"


@design_checks
class InterfaceCheckCollection(CheckCollection):
    service = "interfaces"
    checks: Optional[List[InterfaceCheck]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> "InterfaceCheckCollection":
        def build_check(iface: DeviceInterface):

            # if the interface is not used, meaning it is not part of the
            # design, then there is no profile, and .enabled=False.  No other
            # interface valiation is required for operational state.

            if not iface.used:
                expected_results = InterfaceCheckNotUsedExpectations(used=False)
                if_flags = None

            # if the interface is used (in design) it still could be shutdown
            # (.enabled=False). we would still want to check the reporting speed
            # and descriptions as defined.

            else:
                port_profile = iface.profile.port_profile
                if_flags = iface.profile.profile_flags

                expected_results = InterfaceCheckUsedExpectations(
                    used=True,
                    desc=iface.desc,
                    oper_up=iface.enabled,
                    speed=port_profile.speed if port_profile else None,
                )

                if iface.profile.is_reserved:
                    expected_results.oper_up = None

            return InterfaceCheck(
                check_params=InterfaceCheckParams(
                    interface=iface.name, interface_flags=if_flags
                ),
                expected_results=expected_results,
            )

        collection = InterfaceCheckCollection(
            device=device.name,
            checks=[
                build_check(iface=interface)
                for if_name, interface in device.interfaces.items()
            ],
        )

        # return the checks sorted by the lag interface name
        collection.checks.sort(
            key=lambda tc: DeviceInterface(tc.check_params.interface)
        )
        return collection
