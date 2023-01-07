#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Sequence
from copy import deepcopy

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device.device_group import DeviceGroup, DeviceGroupMember

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["DeviceMLagPairGroup", "DeviceMLagGroupMember"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class DeviceMLagGroupMember(DeviceGroupMember):
    is_mlag_device = True


class DeviceMLagPairGroup(DeviceGroup):
    is_mlag_group = True

    def __init__(
        self,
        name: str,
        devices: Optional[Sequence["DeviceMLagGroupMember"]] = None,
        **kwargs,
    ):

        super(DeviceMLagPairGroup, self).__init__(name, **kwargs)
        for dev in devices:
            self.add_group_member(dev)

    def build(self):
        """
        The build process is used to "copy" any interface profiles defined in
        the MLag Device Group into each of the Device Members (2).  This
        process needs to be called before the calbing process is called so that
        the cabling process can create the cable_peer assignments.
        """

        if not (count := len(self.group_members)) == 2:
            raise RuntimeError(
                f"Unexpected number of devices in device group: {self.name}: {count}"
            )

        # create the association between each of the interfaces defined in the
        # rendudant pair and the associated concrete device. This copies only
        # the interface profile, and no other interface attributes.  The cable
        # associations will be made by the cable planner.

        for if_name, dg_iface_obj in self.interfaces.items():
            for device in self.group_members:

                if not (dg_if_prof := getattr(dg_iface_obj, "profile", None)):
                    continue

                copy_if_pro = deepcopy(dg_if_prof)

                # remove the interface back-ref so that the interface profile
                # can be assigned to the physical device interface; otherwise
                # there is a RuntimeError that checks duplicate assignment.

                copy_if_pro.interface = None

                # now assign the interface profile to the concrete device
                # interface object.

                device.interfaces[if_name].profile = copy_if_pro
