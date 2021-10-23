from typing import List
from copy import deepcopy

from netcad.device import Device


# noinspection PyUnresolvedReferences
class PseudoDevice(Device):
    """
    Attributes
    ---------
    is_pseudo: bool, always True
        Denotes that this device is not real, but rather is used to represent a
        logical construct that is used for programmatic processing.  A Designer
        could use a PseudoDevice, for example, to create a Device subclass that
        represents a redundant-pair of devices, a group of spines, a group of
        leafs, etc.   Such is the case for the DeviceGroupMLagPair.
    """

    is_pseudo = True


class DeviceGroupMLagPair(PseudoDevice):
    is_group = True  # refers to a group

    def __init__(self, name: str, devices: List[Device], **kwargs):
        super(DeviceGroupMLagPair, self).__init__(name, **kwargs)
        self.devices = devices

    def plan(self):
        """
        Apply the design plan for the MLAG pair to the associated devices.  The
        primary function is to find all of the interfaces with profiles and copy
        them to the actual devices in the group.
        """
        if not (count := len(self.devices)) == 2:
            raise RuntimeError(
                f"Unexpected number of devices in device group: {self.name}: {count}"
            )

        # create the association between each of the interfaces defined in the
        # rendudant pair and the associated concrete devices.from

        for if_name, interface in self.interfaces.items():
            for device in self.devices:
                dev_if = device.interfaces[if_name]
                if not (if_prof := getattr(interface, "profile", None)):
                    continue

                copy_if_pro = deepcopy(if_prof)
                copy_if_pro.interface = None
                dev_if.profile = copy_if_pro
