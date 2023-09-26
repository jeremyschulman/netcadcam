from .device import Device
from ..helpers import StrEnum

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
        if not kwargs.get('no_auto_cable'):
            for iface in self.interfaces.values():
                iface.cable_id = self.cable_id(iface.name)

    def cable_id(self, port_id):
        return f"{self.name}_{port_id}"


def attach_host_port(dev: Device, if_name: str, host_name: str | StrEnum, host_port: str):
    host_dev = dev.design.devices[host_name]
    with dev.interfaces[if_name] as iface:
        iface.profile = host_dev.port_connectivity[host_port]
        iface.cable_id = host_dev.cable_id(host_port)

def detach_host_port(dev: Device, if_name: str, host_name: str | StrEnum, host_port: str):
    host_dev = dev.design.devices[host_name]

    with host_dev.interfaces[host_port] as if_host:
        if_host.profile = None
        if_host.cable_id = None

    with dev.interfaces[if_name] as if_net:
        if_net.profile = None
        if_net.cable_id = None
