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
    is_not_managed = True
