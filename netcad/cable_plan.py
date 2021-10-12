from typing import List, Dict
from collections import defaultdict

from netcad.device import Device, DeviceInterface


class CablePlanner(object):
    def __init__(self, name: str):
        self.name = name
        self.devices: List[Device] = list()
        self.cables: Dict[str, List[DeviceInterface]] = defaultdict(list)

    def plan(self):
        raise NotImplementedError()

    def validate(self):
        ifs_by_counts = defaultdict(list)

        for label, interfaces in self.cables.items():
            ifs_by_counts[len(interfaces)].append({label: interfaces})

        proper_cabling = ifs_by_counts.pop(2, None)
        if not proper_cabling:
            raise RuntimeError("No proper cabling", self)

        if ifs_by_counts:
            raise RuntimeError("Improper cabling peer counts", self, ifs_by_counts)

        return True

    def add_devices(self, *devices: Device):
        raise NotImplementedError()


class CableByInterfaceLabel(CablePlanner):
    def add_devices(self, *devices: Device):
        for device in devices:
            for if_name, iface in device.interfaces.items():
                if not iface.label:
                    continue

                self.cables[iface.label].append(iface)

    def plan(self):
        for label, interfaces in self.cables.items():
            pass
