#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional, ClassVar, Any
from itertools import chain
from operator import itemgetter

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, Field

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.device import Device
from netcad.checks import (
    CheckCollection,
    Check,
    CheckResult,
    CheckMeasurement,
    CheckExclusiveList,
    CheckExclusiveResult,
)

# -----------------------------------------------------------------------------
# Module Private Imports
# -----------------------------------------------------------------------------

from ..profiles import InterfaceL2Access, InterfaceL2Trunk, InterfaceVlan
from ..vlan_feat import VlansDesignFeature, DeviceVlanDesignFeature

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "VlanCheckCollection",
    "VlanCheck",
    "VlanCheckResult",
    "VlanExclusiveListCheck",
    "VlanExclusiveListCheckResult",
]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Check VLAN exists with expected set of interfaces
# -----------------------------------------------------------------------------


class VlanCheckExpect(BaseModel):
    name: Optional[str] = Field(
        ..., description="The configured VLAN name; or unchecked if None"
    )
    oper_up: bool = Field(True, description="The operational state of the VLAN")
    interfaces: List[str]


class VlanCheck(Check):
    check_type: str = "vlan"

    class Params(BaseModel):
        vlan_id: int

    class Expect(VlanCheckExpect):
        pass

    check_params: Params
    expected_results: VlanCheckExpect

    def check_id(self) -> str:
        return str(self.check_params.vlan_id)


class VlanCheckResult(CheckResult[VlanCheck]):
    class Measurement(VlanCheckExpect, CheckMeasurement):
        pass

    measurement: Measurement = None


# -----------------------------------------------------------------------------
# Check for exclusive list of Vlans
# -----------------------------------------------------------------------------


class VlanExclusiveListCheck(Check):
    check_type: str = "vlans-exclusive"
    expected_results: CheckExclusiveList[int]


class VlanExclusiveListCheckResult(CheckExclusiveResult[VlanExclusiveListCheck]):
    measurement: CheckExclusiveList = None


# -----------------------------------------------------------------------------
#
#
# -----------------------------------------------------------------------------


@VlansDesignFeature.register_check_collection
class VlanCheckCollection(CheckCollection):
    name: ClassVar[str] = "vlans"
    checks: Optional[List[VlanCheck]]
    config: Optional[Any]

    @classmethod
    def build(
        cls, device: Device, design_feature: "VlansDesignFeature"
    ) -> "VlanCheckCollection":
        """
        Builds the VLAN checks for the given device.

        Parameters
        ----------
        device:
            The device instance

        design_feature: DeviceVlanDesignFeature
            This is actually the _device_ vlan design service, and not
            the top-level vlan design service.
        """

        device_vlans = list(
            chain.from_iterable(
                svc.all_vlans() for svc in device.services_of(DeviceVlanDesignFeature)
            )
        )

        map_vlan_ifaces = dict()
        for vlan in device_vlans:
            map_vlan_ifaces[vlan] = list()

        # iterate through the list of used interfaces on the device, creating
        # the association between VLANs used and the interface.

        for if_name, interface in device.interfaces.used().items():
            if_prof = interface.profile

            if isinstance(
                if_prof, (InterfaceL2Access, InterfaceL2Trunk, InterfaceVlan)
            ):
                vlans = if_prof.vlans_used()
            # elif isinstance(if_prof, InterfaceL2Trunk):
            #     vlans = if_prof.trunk_allowed_vlans()
            else:
                continue

            # iterate across the VlanProfiles for this interface ...

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

        collection = VlanCheckCollection(
            device=device.name,
            exclusive=design_feature.should_check_exclusively(device),
            config=design_feature.config,
            checks=[
                VlanCheck(
                    check_params=VlanCheck.Params(vlan_id=vlan_p.vlan_id),
                    expected_results=VlanCheck.Expect(
                        name=vlan_p.name, interfaces=if_names
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
