# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional
from itertools import chain

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

from netcad.testing_services import TestCases, TestCase
from netcad.testing_services.testing_registry import testing_service


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "VlanTestCase",
    "VlanTestParams",
    "VlanTestExpectations",
    "VlanTestCases",
]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class VlanTestParams(BaseModel):
    vlan_id: int


class VlanTestExpectations(BaseModel):
    vlan: VlanProfile
    interfaces: List[str]


class VlanTestCase(TestCase):
    test_params: VlanTestParams
    expected_results: VlanTestExpectations

    def test_case_id(self) -> str:
        return str(self.test_params.vlan_id)


# -----------------------------------------------------------------------------
#
#
# -----------------------------------------------------------------------------


@testing_service
class VlanTestCases(TestCases):
    service = "vlans"
    tests: Optional[List[VlanTestCase]]

    @classmethod
    def build(cls, device: Device, **kwargs) -> "VlanTestCases":
        from netcad.vlan.vlan_design_service import DeviceVlanDesignService

        # define a mapping of VLAN to the interfaces that are using that Vlan

        map_vlan_ifaces = dict()

        device_vlans = list(
            chain.from_iterable(
                svc.all_vlans() for svc in device.services_of(DeviceVlanDesignService)
            )
        )

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
        # and used by the 'netcam' tooling.

        test_cases = VlanTestCases(
            device=device.name,
            tests=[
                VlanTestCase(
                    test_case="vlan-exists",
                    test_params=VlanTestParams(vlan_id=vlan_p.vlan_id),
                    expected_results=VlanTestExpectations(
                        vlan=vlan_p, interfaces=if_names
                    ),
                )
                for vlan_p, if_names in map_vlan_ifaces.items()
            ],
        )

        # return the test-cases sorted by VLAN-ID
        test_cases.tests.sort(key=lambda tc: tc.test_params.vlan_id)
        return test_cases
