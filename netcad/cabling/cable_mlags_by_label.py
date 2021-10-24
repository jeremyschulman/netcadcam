from typing import Optional

from netcad.device import DeviceInterface
from netcad.device.device_group_mlag import DeviceMLagPairGroup

from .cable_plan import CablePlanner

__all__ = ["CableMLagsByLabel"]


class CableMLagsByLabel(CablePlanner):
    def __init__(self, lables, *vargs, **kwargs):
        super(CableMLagsByLabel, self).__init__(*vargs, **kwargs)
        self.labels = lables

    def validate(self):
        pass

    def apply(self):
        # find the pseudo-device activing as the MLAG redundant pair.  It will have
        # an attribute called `is_group`

        find_mlag_dev = filter(
            lambda d: isinstance(d, DeviceMLagPairGroup), self.devices
        )
        mlag_dev: Optional[DeviceMLagPairGroup]

        if not (mlag_dev := next(find_mlag_dev, None)):
            raise RuntimeError(
                f"Unexpected missing a designated mlag device in cable plan: {self.name}"
            )

        # check if there is more than one, there should not be, but if there is,
        # then it's an error

        if next(find_mlag_dev, None):
            raise RuntimeError(
                f"Unxpected found more than one designated mlag device in cable plan: {self.name}"
            )

        # find the set of interfaces (and labels) that the designated mlag-dev
        # is using that matches the list of allowed labels

        mlag_references = {
            interface.cable_id: interface
            for interface in mlag_dev.interfaces.values()
            if interface.cable_id and interface.cable_id in self.labels
        }

        devices = self.devices.copy()
        devices.remove(mlag_dev)

        # find all of the remote devices that are using the mlag-labels; add these
        # directly to the cabling.

        for device in devices:
            for if_name, iface in device.interfaces.items():
                if not iface.cable_id:
                    continue

                if iface.cable_id in mlag_references:
                    self.add_endpoint(cable_id=iface.cable_id, interface=iface)

        # now bind each of the devices in the mlag-pair to the remotes.  This
        # means that each of the referenced interfaces in two devices in the
        # MLAG pair will point to the same remote interface. (these are
        # port-channels).

        for cable_id, (if_remote,) in self.cables.items():
            if_mlag_ref: DeviceInterface = mlag_references[cable_id]
            for dev in mlag_dev.group_members:
                if_dev = dev.interfaces[if_mlag_ref.name]
                if_dev.cable_peer = if_remote
                self.add_endpoint(cable_id=cable_id, interface=if_dev)

        # at this point there should be three (3) interfaces per cable-id two
        # from the mlag-dev pair-group and one remote.  Call the validate method
        # that will verify this plan.

        self.validate()

        return len(self.cables)
