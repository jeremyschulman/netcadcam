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

from netcad.device import DeviceMLagPairMember, DeviceMLagPairGroup
from netcad.device import InterfaceLag
from netcad.checks import CheckCollection, Check
from netcad.checks import register_collection

from netcad.topology.checks import check_lags as lags

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["MLagCheckCollection", "MLagSystemCheck", "MLagSystemCheckParams"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class MLagSystemCheckParams(BaseModel):
    name = "mlag_system"


class MLagSystemCheck(Check):
    check_type = "mlag_system"
    check_params: MLagSystemCheckParams

    def check_id(self) -> str:
        return self.check_type


@register_collection
class MLagCheckCollection(CheckCollection):
    name = "mlags"
    checks: Optional[List[lags.LagCheck]]

    @classmethod
    def build(
        cls, device: DeviceMLagPairMember, **kwargs
    ) -> Optional["MLagCheckCollection"]:

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

        return MLagCheckCollection(
            device=device.name,
            checks=[
                lags.LagCheck(
                    check_params=lags.LagCheckParams(interface=mlag_iface.name),
                    expected_results=lags.LagCheckExpectations(
                        enabled=mlag_dev.interfaces[mlag_iface.name].enabled,
                        interfaces=[
                            lags.LagCheckExpectedInterfaceStatus(
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
