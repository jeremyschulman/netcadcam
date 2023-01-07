#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Set

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import DeviceInterface
from netcad.cabling.cable_plan import CablePlanner

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["CableMLagsByCableId"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class CableMLagsByCableId(CablePlanner):
    def __init__(self, name: str, cable_ids=Set[str]):
        super(CableMLagsByCableId, self).__init__(name=name)
        self.cable_ids = cable_ids

    def validate(self):
        self.validate_endpoints()

    def build(self, cable_ids: Optional[Set[str]] = None):
        """
        This function is used to build the per-device (not device-group)
        cable_peer associations betweek each of the devices based on the MLag
        cable-IDs assigned to this cable-planner instance.

        Parameters
        ----------
        cable_ids:
            The set of cable-ID values that are presumed assigned to the MLag
            Device Group interfaces, as well as their peers.  The peers could
            either be another MLag device-group instance or a Device instance.
        """

        only_cables = cable_ids or self.cable_ids

        # clear the cable-planner known cables since each call to the 'build'
        # method will create-from-scratch.

        self.cables.clear()

        # ---------------------------------------------------------------------
        # Find MLag Cables from MLag Device Groups
        # ---------------------------------------------------------------------

        # create a dictionary of sets whose key is the MLag Cable ID, and the
        # set members are the device interface objects.  The "device" could
        # either be another MLag device group instance or non Mlagd ("normal")
        # device instance.

        # TBD: why are we making a copy of the devices?
        self_devices = self.devices.copy()

        for dev_obj in self_devices:
            for dev_iface_obj in dev_obj.interfaces.values():
                if (cable_id := dev_iface_obj.cable_id) and (cable_id in only_cables):
                    self.add_endpoint(cable_id=cable_id, interface=dev_iface_obj)

        # ---------------------------------------------------------------------
        # Cabling
        # ---------------------------------------------------------------------

        iface_a: DeviceInterface
        iface_b: DeviceInterface

        for cable_id, (iface_a, iface_b) in self.cables.items():

            # first assign the cable_peer to each other so that the
            iface_a.cable_peer = iface_b
            iface_b.cable_peer = iface_a

            # if iface_a on a MLag device-group, then we need to create the
            # cable_peer on each of the member devices to iface_b

            if iface_a.device.is_mlag_group:
                for mlag_dev in iface_a.device.group_members:
                    mlag_dev_iface = mlag_dev.interfaces[iface_a.name]
                    mlag_dev_iface.cable_peer = iface_b
                    self.add_endpoint(cable_id, mlag_dev_iface)

            # likewise for iface_b ...

            if iface_b.device.is_mlag_group:
                for mlag_dev in iface_b.device.group_members:
                    mlag_dev_iface = mlag_dev.interfaces[iface_b.name]
                    mlag_dev_iface.cable_peer = iface_a
                    self.add_endpoint(cable_id, mlag_dev_iface)

        self.validate()
