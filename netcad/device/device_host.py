# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .device import Device, DeviceInterface
from ..helpers import StrEnum

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["HostDevice", "attach_host_port", "detach_host_port"]


# noinspection PyUnresolvedReferences
class _HostDevice(Device):
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
    is_not_managed = True


class HostDevice(_HostDevice):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.port_connectivity = {}
        if not kwargs.get("no_auto_cable"):
            for iface in self.interfaces.values():
                iface.cable_id = self.cable_id(iface.name)

    def cable_id(self, port_id):
        return f"{self.name}_{port_id}"


def attach_host_port(
    dev: Device, if_name: str, host_name: str | StrEnum, host_port: str
) -> Tuple[DeviceInterface, DeviceInterface]:
    """
    This function is used to "connect" a network device to a host devie given
    the call parameters.  This function will return a tuple of the device
    interfaces. The first one being the network interface and the second being
    the host interface.

    This function presumes that the host device has been initialized such that
    the host_port value has a device InterfaceProfile instance assign so that
    it can be used by the network interface profile.

    Parameters
    ----------
    dev:
        The network device instance
    if_name:
        The network device interface name where the host will be attached

    host_name:
        The name of the host.  This value will be used to look up the host
        device instance in the design.  This assumes that the network device
        has the design attribute set.
    host_port:
        The host interface name.

    Returns
    -------
    tuple of device interfaces as described
    """
    host_dev = dev.design.devices[host_name]
    with dev.interfaces[if_name] as iface:
        iface.profile = host_dev.port_connectivity[host_port]
        iface.cable_id = host_dev.cable_id(host_port)

    # return the network device interface, host device interface
    return iface, host_dev.interfaces[host_port]


def detach_host_port(
    dev: Device, if_name: str, host_name: str | StrEnum, host_port: str
) -> Tuple[DeviceInterface, DeviceInterface]:
    """
    This function is used to "disconnect" a network device from a host devie given
    the call parameters.  This function will return a tuple of the device
    interfaces. The first one being the network interface and the second being
    the host interface.

    Parameters
    ----------
    dev:
        The network device instance
    if_name:
        The network device interface name where the host was attached

    host_name:
        The name of the host.  This value will be used to look up the host
        device instance in the design.  This assumes that the network device
        has the design attribute set.

    host_port:
        The host interface name.

    Returns
    -------
    tuple of device interfaces as described
    """

    host_dev = dev.design.devices[host_name]

    with host_dev.interfaces[host_port] as if_host:
        if_host.profile = None
        if_host.cable_id = None

    with dev.interfaces[if_name] as if_net:
        if_net.profile = None
        if_net.cable_id = None

    # return the network device interface, host device interface
    return if_net, if_host
