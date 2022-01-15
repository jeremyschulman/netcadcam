#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional
from typing import TYPE_CHECKING
from itertools import chain
from operator import itemgetter

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.device import Device
from netcad.checks import CheckCollection, Check
from netcad.checks.check_registry import register_collection

if TYPE_CHECKING:
    from netcad.device.l3_interfaces import InterfaceVlan
    from netcad.vlans.vlan_design_service import VlansDesignService
    from netcad.vlans import VlanProfile
    from netcad.vlans.profiles.l2_interfaces import InterfaceL2Access, InterfaceL2Trunk


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "VlanCheck",
    "VlanCheckParams",
    "VlanCheckExpectations",
    "VlanCheckCollection",
    "VlanCheckExclusiveList",
    "VlanExclusiveListExpectations",
]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class VlanCheckParams(BaseModel):
    vlan_id: int


class VlanCheckExpectations(BaseModel):
    vlan: "VlanProfile"
    interfaces: List[str]


class VlanCheck(Check):
    check_type = "interface"
    check_params: VlanCheckParams
    expected_results: VlanCheckExpectations

    def check_id(self) -> str:
        return str(self.check_params.vlan_id)


# -----------------------------------------------------------------------------
# Check for exclusive list of Vlans
# -----------------------------------------------------------------------------


class VlanExclusiveListExpectations(BaseModel):
    vlans: List["VlanProfile"]


class VlanCheckExclusiveList(Check):
    check_type = "exclusive_list"
    expected_results: VlanExclusiveListExpectations

    def check_id(self) -> str:
        return self.check_type


# -----------------------------------------------------------------------------
#
#
# -----------------------------------------------------------------------------


@register_collection
class VlanCheckCollection(CheckCollection):
    name = "vlans"
    checks: Optional[List[VlanCheck]]
    exclusive: Optional[VlanCheckExclusiveList]

    @classmethod
    def build(
        cls, device: Device, design_service: "VlansDesignService"
    ) -> "VlanCheckCollection":
        from netcad.vlans.vlan_design_service import DeviceVlanDesignService

        device_vlans = list(
            chain.from_iterable(
                svc.all_vlans() for svc in device.services_of(DeviceVlanDesignService)
            )
        )

        map_vlan_ifaces = dict()
        for vlan in device_vlans:
            map_vlan_ifaces[vlan] = list()

        # iterate through the list of used interfaces on the device, creating
        # the association between VLANs used and the interface.

        for if_name, interface in device.interfaces.used().items():
            if_prof = interface.profile

            if isinstance(if_prof, (InterfaceL2Access, InterfaceVlan)):
                vlans = if_prof.vlans_used()
            elif isinstance(if_prof, InterfaceL2Trunk):
                vlans = if_prof.trunk_allowed_vlans()
            else:
                continue

            for vlan in vlans:

                # put a guard-rail check on used interface vlans vs. device
                # declared vlans by design. it is possible that the Designer
                # invoked the "vlans build" method before all VLANs in the
                # desgin were made by their design files.  In this case log the
                # error and raise the exception so the Designer can fix their
                # design files.

                if vlan not in map_vlan_ifaces:
                    log = get_logger()
                    err_msg = (
                        f"{device.name}: Missing expected VLAN: {vlan.name}, found on interface {if_name}."
                        "Error likely due to when the vlan service build method was invoked."
                    )
                    log.error(err_msg)
                    raise RuntimeError(err_msg)

                map_vlan_ifaces[vlan].append(if_name)

        # Create the instance of the Vlans check collections so that it can be
        # stored and used by the 'netcam' tooling.

        # create the check for exclusive list of Vlans, by default
        # TODO: make this control configurable in the DesignService.

        exl_check = VlanCheckExclusiveList(
            expected_results=VlanExclusiveListExpectations(vlans=list(map_vlan_ifaces))
        )

        collection = VlanCheckCollection(
            device=device.name,
            exclusive=exl_check,
            checks=[
                VlanCheck(
                    check_type="interfaces",
                    check_params=VlanCheckParams(vlan_id=vlan_p.vlan_id),
                    expected_results=VlanCheckExpectations(
                        vlan=vlan_p, interfaces=if_names
                    ),
                )
                for vlan_p, if_names in sorted(
                    map_vlan_ifaces.items(), key=itemgetter(0)
                )
            ],
        )

        # return the test-cases sorted by VLAN-ID
        collection.checks.sort(key=lambda tc: tc.check_params.vlan_id)
        return collection
