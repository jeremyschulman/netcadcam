from typing import Dict, Hashable, Set
from collections import defaultdict

from netcad.device import Device, DeviceInterface
from netcad.registry import Registry


class CablePlanner(Registry):
    def __init__(self, name: str):
        self.registry_add(name, self)

        self.name = name
        self.devices: Set[Device] = set()
        self.cables: Dict[Hashable, set] = defaultdict(set)
        self.validated = False

    def add_devices(self, *devices: Device):
        self.devices.update(devices)

    def add_endpoint(self, cable_id, interface: DeviceInterface):
        self.cables[cable_id].add(interface)

    def validate(self):
        """
        Validates the cabling plan by ensureing that each cable contains exactly
        two device interface instances.  If the plan is valid, then the
        `validated` attribute will be set to True.

        If there are no validate cables, meaning, no cables with two end-points,
        then an exception is raised.

        If there are calbing records with count != 2, then an exception is raised.

        Returns
        -------
        The number of cables.
        """
        ifs_by_counts = defaultdict(list)

        for label, interfaces in self.cables.items():
            ifs_by_counts[len(interfaces)].append({label: interfaces})

        proper_cabling = ifs_by_counts.pop(2, None)
        if not proper_cabling:
            raise RuntimeError("No cabling", self, ifs_by_counts)

        if ifs_by_counts:
            raise RuntimeError("Improper cabling peer counts", self, ifs_by_counts)

        self.validated = True
        return len(self.cables)

    @classmethod
    def find_cables_by_device(cls, device: Device):
        device_cables = list()

        cablers = cls.registry_list(subclasses=True)

        for each_name in cablers:
            cabler: CablePlanner = cls.registry_get(each_name)

            for cable_id, endpoints in cabler.cables.items():
                if any(map(lambda e: e.device == device, endpoints)):
                    device_cables.append((cable_id, endpoints))

        return device_cables

    def apply(self):
        """
        Apply the algorithm of performing the cable plan.  The Subclass must
        implement this method to perform the actual "cabling plan".   The Caller
        should call the `validate()` method after the apply ... at some point,
        to ensure the plan is valid.  Some "cable planners" may implement a
        "multiple stage apply" algoritm.  In these cases the Caller would invoke
        `validate()` after all of the apply functions are completed.

        Returns
        -------
        The number of cables applied.

        Raises
        ------
        RuntimeError:
            The subclass method should raise this exception in the even there is
            any issue in the apply execution.
        """
        raise NotImplementedError()


class CableByInterfaceLabel(CablePlanner):
    def apply(self):
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
                if not iface.label:
                    continue

                self.add_endpoint(cable_id=iface.label, interface=iface)

        # now invoke the validate() method directly before associating the cable
        # peering relationships.

        self.validate()

        # now associate the cable-peer relationships.

        for if_a, if_b in self.cables.values():
            if_a.cable_peer = if_b
            if_b.cable_peer = if_a

        return len(self.cables)
