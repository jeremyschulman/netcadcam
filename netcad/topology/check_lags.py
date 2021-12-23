# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional
from collections import defaultdict

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device, DeviceInterface
from netcad.checks import CheckCollection, Check
from netcad.device import InterfaceLag

from netcad.checks import design_checks

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "LagCheckCollection",
    "LagCheck",
    "LagCheckParams",
    "LagCheckExpectations",
    "LagCheckExpectedInterfaceStatus",
]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class LagCheckParams(BaseModel):
    interface: str


class LagCheckExpectedInterfaceStatus(BaseModel):
    interface: str
    enabled: bool


class LagCheckExpectations(BaseModel):
    enabled: bool
    interfaces: List[LagCheckExpectedInterfaceStatus]


class LagCheck(Check):
    check_params: LagCheckParams
    expected_results: LagCheckExpectations

    def check_id(self) -> str:
        return str(self.check_params.interface)


@design_checks
class LagCheckCollection(CheckCollection):
    service = "lags"
    checks: Optional[List[LagCheck]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> Optional["LagCheckCollection"]:

        # scan the device interfaces looking for LAGs.  Create a dictionary
        # key=lag-if-name, value=list of member interfaces.

        lag_interfaces = defaultdict(list)

        for if_name, interface in device.interfaces.used().items():
            if not isinstance(interface.profile, InterfaceLag):
                continue

            # TODO: not sure why this is here now; should
            #       just be using interface
            # if_lag = interface.profile.lag_parent
            # if not if_lag:
            #     breakpoint()
            #     x=1

            lag_interfaces[interface.name].extend(
                iface for iface in interface.profile.if_lag_members
            )

        # if no lags found, then return None so that the checks file is not
        # generated.

        if not lag_interfaces:
            return None

        # create the collection of checks using the formulated dictionary.

        collection = LagCheckCollection(
            device=device.name,
            checks=[
                LagCheck(
                    check_type="lag",
                    check_params=LagCheckParams(interface=lag_name),
                    expected_results=LagCheckExpectations(
                        enabled=device.interfaces[lag_name].enabled,
                        interfaces=[
                            LagCheckExpectedInterfaceStatus(
                                interface=each_interface.name,
                                enabled=each_interface.enabled,
                            )
                            for each_interface in lag_interfaces
                        ],
                    ),
                )
                for lag_name, lag_interfaces in lag_interfaces.items()
            ],
        )

        # return the collection sorted by the lag interface name

        collection.checks.sort(
            key=lambda tc: DeviceInterface(tc.check_params.interface)
        )

        return collection
