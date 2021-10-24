# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .device import Device


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["PseudoDevice", "DeviceGroup", "DeviceGroupMember"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


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


class DeviceGroup(PseudoDevice):
    is_group = True

    def __init__(self, *vargs, **kwargs):
        super(DeviceGroup, self).__init__(*vargs, **kwargs)
        self._group_members = set()

    @property
    def group_members(self):
        return self._group_members

    def add_group_member(self, device: "DeviceGroupMember"):
        device.device_group = self
        self._group_members.add(device)


class DeviceGroupMember(Device):
    is_group_member = True

    def __init__(self, *vargs, **kwargs):
        self.device_group = None
        super(DeviceGroupMember, self).__init__(*vargs, **kwargs)
