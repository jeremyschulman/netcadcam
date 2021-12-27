#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional
from copy import deepcopy

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .device_group import DeviceGroup, DeviceGroupMember

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["DeviceMLagPairGroup", "DeviceMLagPairMember"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class DeviceMLagPairGroup(DeviceGroup):
    def __init__(
        self,
        name: str,
        devices: Optional[List["DeviceMLagPairMember"]] = None,
        **kwargs,
    ):

        super(DeviceMLagPairGroup, self).__init__(name, **kwargs)
        for dev in devices:
            self.add_group_member(dev)

    def plan(self):
        """
        Apply the design plan for the MLAG pair to the associated devices.  The
        primary function is to find all of the interfaces with profiles and copy
        them to the actual devices in the group.
        """
        if not (count := len(self.group_members)) == 2:
            raise RuntimeError(
                f"Unexpected number of devices in device group: {self.name}: {count}"
            )

        # create the association between each of the interfaces defined in the
        # rendudant pair and the associated concrete devices.from

        for if_name, interface in self.interfaces.items():
            for device in self.group_members:
                dev_if = device.interfaces[if_name]
                if not (if_prof := getattr(interface, "profile", None)):
                    continue

                copy_if_pro = deepcopy(if_prof)
                copy_if_pro.interface = None
                dev_if.profile = copy_if_pro


class DeviceMLagPairMember(DeviceGroupMember):

    # -------------------------------------------------------------------------
    #
    #                            Device Overrides
    #
    # -------------------------------------------------------------------------

    def testing_services(self) -> List[str]:
        """DeviceGroupMLagPair devices have 'mlags' test cases"""
        tests = super(DeviceMLagPairMember, self).testing_services()
        tests.append("mlags")
        return tests
