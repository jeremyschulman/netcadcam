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

from netcad.device import DeviceMLagPairMember, DeviceMLagPairGroup
from netcad.device import InterfaceLag
from netcad.checks import CheckCollection, Check
from netcad.checks import design_checks

from . import tc_lags as lags


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["MLagTestCases", "MLagSystemTestCase", "MLagSystemTestParams"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class MLagSystemTestParams(BaseModel):
    name = "mlag_system"


class MLagSystemTestCase(Check):
    check_type = "mlag_system"
    check_params: MLagSystemTestParams

    def check_id(self) -> str:
        return self.check_type


@design_checks
class MLagTestCases(CheckCollection):
    service = "mlags"
    checks: Optional[List[lags.LagTestCase]]

    @classmethod
    def build(cls, device: DeviceMLagPairMember, **kwargs) -> Optional["MLagTestCases"]:

        # find all of the LAG interfaces defined on the psuedo MLAG devic

        if not hasattr(device, "device_group"):
            return None

        mlag_dev: DeviceMLagPairGroup = device.device_group
        mlag_interfaces = sorted(
            (
                interface
                for interface in mlag_dev.interfaces.used().values()
                if isinstance(interface.profile, InterfaceLag)
            )
        )

        # TODO: for now, there is an _archiectual decision_ that both devices in
        #       the MLAG group will use the same port-channels within an MLAG
        #       interface. meaning MLAG 1 = Port-Channel1 on both device (if
        #       this was an Arista device).

        test_cases = MLagTestCases(
            device=device.name,
            checks=[
                lags.LagTestCase(
                    check_params=lags.LagTestParams(interface=mlag_iface.name),
                    expected_results=lags.LagTestExpectations(
                        enabled=mlag_dev.interfaces[mlag_iface.name].enabled,
                        interfaces=[
                            lags.LagTestExpectedInterfaceStatus(
                                interface=each_interface.name,
                                enabled=each_interface.enabled,
                            )
                            for each_interface in [
                                mlag_iface,
                                mlag_iface,
                            ]  # peer, remote; same name
                        ],
                    ),
                )
                for mlag_iface in mlag_interfaces
            ],
        )

        return test_cases
