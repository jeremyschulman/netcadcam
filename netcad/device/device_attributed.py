from .device import Device


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


class DeviceNotManaged(Device):
    """
    Denotes a device that is part of the network design, but is not managed in any way
    such that checks/checking is not performed.  Config generation is not performed.
    """

    is_not_managed = True
