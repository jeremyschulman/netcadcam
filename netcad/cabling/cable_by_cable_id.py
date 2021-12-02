from .cable_plan import CablePlanner


class CableByCableId(CablePlanner):
    def build(self):
        """
        The `apply` function will create the cable associations between
        the devices.  The Caller is assumed to have called the `validate`
        prior to calling `plan`.

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
                if not iface.cable_id:
                    continue
                self.add_endpoint(cable_id=iface.cable_id, interface=iface)

        # now invoke the validate() method directly before associating the cable
        # peering relationships.

        self.validate()

        # now associate the cable-peer relationships.

        for if_a, if_b in self.cables.values():
            if_a.cable_peer = if_b
            if_b.cable_peer = if_a

        return len(self.cables)
