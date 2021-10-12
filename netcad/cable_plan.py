from typing import List, Dict
from collections import defaultdict

from netcad.device import Device, DeviceInterface
from netcad.helpers import Registry


class CablePlanner(Registry):
    def __init__(self, name: str):
        self.registry_add(name, self)

        self.name = name
        self.devices: List[Device] = list()
        self.cables: Dict[str, List[DeviceInterface]] = defaultdict(list)
        self.validated = False

    def apply(self):
        raise NotImplementedError()

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

    def add_devices(self, *devices: Device):
        raise NotImplementedError()


class CableByInterfaceLabel(CablePlanner):
    def add_devices(self, *devices: Device):
        for device in devices:
            for if_name, iface in device.interfaces.items():
                if not iface.label:
                    continue

                self.cables[iface.label].append(iface)

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
        if not self.validated:
            raise RuntimeError(
                "This plan has not been validated, call the validate() method."
            )

        for if_a, if_b in self.cables.values():
            if_a.cable_peer = if_b
            if_b.cable_peer = if_a
