#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Dict, Hashable, Set
from collections import defaultdict

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device, DeviceInterface
from netcad.registry import Registry

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["CablePlanner"]


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

    def validate_endpoints(self):
        """
        This routine validates that, for each cable, all of the endpoints
        associated with that cable have a matching interface enabled
        setting, and a matching interface speed setting.

        Returns
        -------
        True when validated

        Raises
        ------
        RuntimeErrror
            Upon finding an invalid cable.
        """

        def if_list_info():
            return ", ".join(
                [
                    "{}:{} {}".format(
                        iface.device.name,
                        iface.name,
                        "enabled" if iface.enabled else "disabled",
                    )
                    for iface in if_endpoints
                ]
            )

        for cable_id, if_endpoints in self.cables.items():

            if len(set(ep.enabled for ep in if_endpoints)) != 1:

                raise RuntimeError(
                    f"Not all interfaces in cable id {cable_id} are set "
                    f"to the same enabled value: {if_list_info()}"
                )

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

        if ifs_by_counts:
            from pprint import pformat

            content = pformat(dict(ifs_by_counts), indent=3)
            raise RuntimeError(
                f"Cable plan: {self.name}: Improper cabling peer counts:\n{content}",
            )
        elif not proper_cabling:
            raise RuntimeError("No cabling", self, ifs_by_counts)

        self.validate_endpoints()
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

    def build(self):
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
