#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from uuid import uuid4
from .cable_plan import CablePlanner


class CableByCableId(CablePlanner):
    def build(self):
        """
        The build function will create the cable associations between the
        devices.  The Caller is assumed to have called the `validate` prior to
        calling `plan`.

        Raises
        ------
        RuntimeError
            If the cabling plan has not been validated.

        Returns
        -------
        Number of cablee
        """

        # For every device interface that has an assigned label, use that label
        # to add the interface to the cabling collection using the label as the
        # cable-id.

        for device in self.devices:
            for if_name, iface in device.interfaces.items():

                # if the interface has been assigned a cable_peer without using
                # the cable_id value, ***and*** the remote interface is the
                # cable peer, then auto-gen a cable-id so that it shows up in
                # the cabling report.

                if (rmt_iface := iface.cable_peer) and not iface.cable_id:
                    if rmt_iface.cable_peer == iface:
                        iface.cable_id = rmt_iface.cable_id = uuid4()

                # if the interface is not assigned a cable_id, then skip it.

                if not iface.cable_id:
                    continue

                self.add_endpoint(cable_id=iface.cable_id, interface=iface)

        # now invoke the `validate()` method directly before associating the
        # cable peering relationships.

        self.validate()

        # now associate the cable-peer relationships.

        for if_a, if_b in self.cables.values():
            if_a.cable_peer = if_b
            if_b.cable_peer = if_a

        return len(self.cables)
