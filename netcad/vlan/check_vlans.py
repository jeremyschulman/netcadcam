# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional
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
from netcad.vlan import VlanProfile

from netcad.device.l2_interfaces import InterfaceL2Access, InterfaceL2Trunk
from netcad.device.l3_interfaces import InterfaceVlan

from netcad.checks import CheckCollection, Check
from netcad.checks.check_registry import design_checks


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "VlanCheck",
    "VlanCheckParams",
    "VlanCheckExpectations",
    "VlanCheckCollection",
    "VlanCheckExclusiveList",
]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class VlanCheckParams(BaseModel):
    vlan_id: int


class VlanCheckExpectations(BaseModel):
    vlan: VlanProfile
    interfaces: List[str]


class VlanCheck(Check):
    check_type = "interface"
    check_params: VlanCheckParams
    expected_results: VlanCheckExpectations

    def check_id(self) -> str:
        return str(self.check_params.vlan_id)


class VlanCheckExclusiveList(Check):
    check_type = "exclusive_list"
    check_params: Optional[BaseModel] = None
    expected_results: Optional[BaseModel] = None

    def check_id(self) -> str:
        return self.check_type


# -----------------------------------------------------------------------------
#
#
# -----------------------------------------------------------------------------


@design_checks
class VlanCheckCollection(CheckCollection):
    service = "vlans"
    checks: Optional[List[VlanCheck]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> "VlanCheckCollection":
        from netcad.vlan.vlan_design_service import DeviceVlanDesignService

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

        # Create the instance of the Vlans Test Cases so that it can be stored
        # and used by the 'netcam' tooling.  Keep the test cases sorted by
        # VLAN-ID value; which is how the VlanProfile object is sortable.

        test_cases = VlanCheckCollection(
            device=device.name,
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
        test_cases.checks.sort(key=lambda tc: tc.check_params.vlan_id)
        return test_cases
