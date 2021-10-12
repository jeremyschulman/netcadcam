from typing import Optional, TYPE_CHECKING
import re

if TYPE_CHECKING:
    from netcad.interface_profile import InterfaceProfile


_re_find_numbers = re.compile(r"\d+")

# short-name is the first two characters of the name, followed by the remaining
# interface numbers.  For example, "Ethernet49/1" turns into "Et49/1"

_re_short_name = re.compile(r"(\D\D)\D+(\d.*)")


class DeviceInterface(object):
    def __init__(
        self,
        name: str,
        profile: Optional["InterfaceProfile"] = None,
        used: Optional[bool] = True,
        desc: Optional[str] = "",
        label: Optional[str] = None,
        interfaces=None,
    ):
        self.name = name
        self.port_numbers = tuple(map(int, _re_find_numbers.findall(name)))
        self.short_name = "".join(_re_short_name.match(name).groups())
        self.profile = profile
        self.used = used
        self.desc = desc
        self.label = label

        self.cable_peer: Optional[DeviceInterface] = None

        # `interfaces` is a back-reference to the collection of all interfaces;
        # see Interfaces class definition.  This instance will be assigned when
        # the actual interface is instantiated.  This back-reference will then
        # provide access to the parent device.  See __repr__ for example usage.

        self.interfaces = interfaces

    @property
    def device(self):
        """return the device instance associated with this interface"""
        return self.interfaces.device

    @property
    def device_ifname(self) -> str:
        """
        Returns the short-form device interface name.  The format is the
        associated <device.name>-<interface.short_name in lower-case>.

        For example, if the associated device name was "router1" and the
        interface name was "Ethernet1/2", then this function would return
        'router1-et1/2'.

        Raises
        -------
        RuntimeError
            When no device is assigned to the interface.  This is an unusual
            case since a device will automatically assigned during the
            defaultdict process of the Device object.  Added this raise for
            dev-testing purposes.
        """
        parent = self.interfaces
        ifn_lc = self.short_name.lower()
        device_name = (
            parent.device.name if parent.device else parent.device_cls.__name__
        )
        return f"{device_name}-{ifn_lc}"

    def __repr__(self):
        parent = self.interfaces
        name = (
            f"{parent.device.name}.{self.name}"
            if parent.device
            else f"{parent.device_cls.__name__}.{self.name}"
        )

        if self.profile:
            return f"{name} {self.profile.__class__.__name__}"

        if self.used is False:
            return f"{name} Unused"

        return f"{name} Unassigned-Profile"
