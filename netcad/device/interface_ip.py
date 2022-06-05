from ipaddress import IPv4Address, IPv6Address

from .device_interface import DeviceInterface


class InterfaceIPv4(IPv4Address):
    __slots__ = "interface"


class InterfaceIPv6(IPv6Address):
    __slots__ = "interface"


__all__ = ["InterfaceIP", "to_interface_ip"]


InterfaceIP = InterfaceIPv4 | InterfaceIPv6


def to_interface_ip(
    ip: IPv4Address | IPv6Address, interface: DeviceInterface
) -> InterfaceIP:
    """
    This function returns an "augmented" ip_address instance value that
    includes an 'interface' attribute.  This interface attribute is the
    DeviceInterface instance that is hosting the IP address.  This construct is
    very useful when manipulating IP address values and one needs to know the
    bound interface.

    Parameters
    ----------
    ip:
        An ipaddress instance, either IPv4 or IPv6

    interface:
        The DeviceInterface instance that is hosting this IP address
    """
    if_ip = (InterfaceIPv4 if isinstance(ip, IPv4Address) else InterfaceIPv6)(ip)
    if_ip.interface = interface
    return if_ip
