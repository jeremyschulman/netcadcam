#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Sequence, Optional
from operator import attrgetter
from itertools import filterfalse

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import DeviceInterface
from .cable_plan import CablePlanner

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
    def __init__(self, name: str, cable_ids=Sequence[str]):
        super(CableMLagsByCableId, self).__init__(name=name)
        self.cable_ids = cable_ids

    def validate(self):
        self.validate_endpoints()

    def build(self, cable_ids: Optional[Sequence[str]] = None):
        only_cables = cable_ids or self.cable_ids
        self.cables.clear()

        # find the pseudo-device activing as the MLAG redundant pair.  If one is
        # not found, then raise an exception.

        if not (found_mlag_dev := [dev for dev in self.devices if dev.is_pseudo]):
            raise RuntimeError(
                f"Unexpected missing a designated mlag device in cable plan: {self.name}"
            )

        # check if there is more than one, there should not be, but if there is,
        # then it's an error

        if len(found_mlag_dev) > 1:
            raise RuntimeError(
                f"Unxpected found more than one designated mlag device in cable plan: {self.name}"
            )

        # create a mapping of the mlag cable-id to the mlag device interface
        # bound to that cable.

        mlag_dev = found_mlag_dev[0]
        mlag_references = {
            interface.cable_id: interface
            for interface in mlag_dev.interfaces.values()
            if interface.cable_id and interface.cable_id in only_cables
        }

        devices = self.devices.copy()
        mlag_dev_names = set(map(attrgetter("name"), mlag_dev.group_members))

        devices = set(
            filterfalse(lambda d: d is mlag_dev or d.name in mlag_dev_names, devices)
        )

        # find all of the remote devices that are using the mlag-labels; add
        # these directly to the cabling.  Each cable-ID should have a *SINGLE*
        # remote reference; for example to an individual interface or to a LAG.

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

        for cable_id, endpoints in self.cables.items():
            if_remote = next(iter(endpoints))

            if not isinstance(if_remote, DeviceInterface):
                raise RuntimeError(f"Unexpected mlag remote cable: {if_remote}")

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
