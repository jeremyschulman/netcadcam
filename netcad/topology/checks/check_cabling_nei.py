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

from netcad.device import Device, DeviceInterface, HostDevice
from netcad.checks import CheckCollection, Check
from netcad.checks import register_collection

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "InterfaceCablingCheckCollection",
    "InterfaceCablingCheck",
    "InterfaceCablingdExpectations",
    "InterfaceCablingCheckParams",
    "NoValidateCabling",
]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class NoValidateCablingSential:
    def __str__(self):
        return "no-validate"


# sentical value to mark the interface.cable_peer.cable_port_id so that this
# checking collection does to perform a cable check on that interface.

NoValidateCabling = NoValidateCablingSential()

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class InterfaceCablingCheckParams(BaseModel):
    interface: str


class InterfaceCablingdExpectations(BaseModel):
    device: str
    port_id: str


class InterfaceCablingCheck(Check):
    check_type = "cabling"
    check_params: InterfaceCablingCheckParams
    expected_results: InterfaceCablingdExpectations

    def check_id(self) -> str:
        return str(self.check_params.interface)


@register_collection
class InterfaceCablingCheckCollection(CheckCollection):
    name = "cabling"
    checks: Optional[List[InterfaceCablingCheck]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> "InterfaceCablingCheckCollection":

        # only used physical interfaces that have a cabling peer relationship.
        # exclude any interfaces that are disabled, since the cabling tests will
        # use a layer-2 protocol (LLDP or CDP) to validate the neighbor
        # relationship.  If the peering cable port-id is marked as "no-validate"
        # using the sential object, then skip that one too.

        def should_check_lldp(_iface: DeviceInterface):
            return (
                _iface.cable_peer
                and not _iface.profile.is_virtual
                and not isinstance(_iface.cable_peer.device, HostDevice)
                and _iface.cable_peer.cable_port_id is not NoValidateCabling
            )

        interfaces: List[DeviceInterface] = sorted(
            filter(
                should_check_lldp,
                device.interfaces.used(include_disabled=False).values(),
            )
        )

        return InterfaceCablingCheckCollection(
            exclusive=False,
            device=device.name,
            checks=[
                InterfaceCablingCheck(
                    check_params=InterfaceCablingCheckParams(interface=interface.name),
                    expected_results=InterfaceCablingdExpectations(
                        device=interface.cable_peer.device.name,
                        port_id=interface.cable_peer.cable_port_id,
                    ),
                )
                for interface in interfaces
            ],
        )
