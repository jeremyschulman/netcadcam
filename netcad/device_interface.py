from typing import Optional, TYPE_CHECKING
import re

if TYPE_CHECKING:
    from netcad.interface_profile import InterfaceProfile


_re_find_numbers = re.compile(r"\d+")
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
        if not self.device:
            raise RuntimeError("Missing: device not assigned")

        return f"{self.device.name}-{self.short_name.lower()}"

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
