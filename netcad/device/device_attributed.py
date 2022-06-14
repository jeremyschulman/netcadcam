from .device import Device


# noinspection PyUnresolvedReferences
class HostDevice(Device):
    """
    Denotes a Host device that is connected to the network.  This device is not
    managemed by the NetCAD system.  The Host device is used to represent
    connectivity related design aspects.

    Attributes
    ---------
    is_host: bool, always True
    is_not_managed: bool, always True
    """

    is_host = True
    is_pseudo = True


# noinspection PyUnresolvedReferences
class DeviceNonExclusive(Device):
    """
    Denotes a device that is not exclusively designed-management by NETCAD. For
    example, a Designer may have devices in their design that are partially
    managemed by NetCAD and partially managed by another system, or human.

    When a device is denoted as "non-exclusive" the design checks will not
    include "exclusive-list" type checks.
    """

    is_not_exclusive = True
