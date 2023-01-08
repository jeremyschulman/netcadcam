#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

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
from netcad.checks import CheckCollection, Check, CheckResult, CheckMeasurement
from netcad.device.profiles import InterfaceLag

from netcad.checks import register_collection

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "LagCheckCollection",
    "LagCheck",
    "LagCheckResult",
    "LagCheckExpectedInterfaceStatus",
]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class LagCheckExpectedInterfaceStatus(BaseModel):
    interface: str      # interface name
    enabled: bool       # if the interface is enabled in design


class LagCheck(Check):
    check_type = "lag"

    class Params(BaseModel):
        interface: str      # interface name of LAG

    class Expect(BaseModel):
        enabled: bool       # if the LAG is enabled in design
        interfaces: List[LagCheckExpectedInterfaceStatus]

    check_params: Params
    expected_results: Expect

    def check_id(self) -> str:
        return str(self.check_params.interface)


class LagCheckResult(CheckResult[LagCheck]):
    class Measurement(LagCheck.Expect, CheckMeasurement):
        pass

    measurement: Measurement = None


@register_collection
class LagCheckCollection(CheckCollection):
    name = "lags"
    checks: Optional[List[LagCheck]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> Optional["LagCheckCollection"]:

        # scan the device interfaces looking for LAGs.  Create a dictionary
        # key=lag-if-name, value=list of member interfaces.

        lag_interfaces = defaultdict(list)

        for if_name, interface in device.interfaces.used().items():
            if not isinstance(interface.profile, InterfaceLag):
                continue

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
                    check_params=LagCheck.Params(interface=lag_name),
                    expected_results=LagCheck.Expect(
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
            key=lambda tc: DeviceInterface(
                tc.check_params.interface, interfaces=device.interfaces
            )
        )

        return collection
