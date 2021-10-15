# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, TYPE_CHECKING
import re

if TYPE_CHECKING:
    from netcad.interface_profile import InterfaceProfile

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["DeviceInterface"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


_re_find_numbers = re.compile(r"\d+")

# short-name is the first two characters of the name, followed by the remaining
# interface numbers.  For example, "Ethernet49/1" turns into "Et49/1"

_re_short_name = re.compile(r"(\D\D)\D+(\d.*)")


class DeviceInterface(object):
    """

    Attributes
    ----------
    name : str
        The full-name of the interface, for example "Ethernet49/1"

    short_name: str
        A shortened version of the full-name that is composed of only the first
        two letters, followed by the numberical portion. An interface name
        "Ethernet50/1" would have a short_name "Et50/1".

    used : bool
        Denotes whether or not the interface should be administratively
        enabled(True) or disabled(False).

    port_numbers: Tuple[Int]
        A tuple of only the numbers in the interface name. These are useful for
        numerical sorting purpose. An interface with name "GigabitEtherent1/0/2"
        would have port_numbers = (1,0,2).

    sort_key: Tuple[str, int, ...]
        A tuple that can be used for sorting a list of interfaces.  The first
        value in the tuple is the first two characters of the name.  The
        remaning values are the port_numbers.  An interface name "Ethernet49"
        would have a sort_key ("et", 49), for example.

    cable_peer: DeviceInterface
        The instance of the device-interface on the far end of a cable
        relationship.

    interfaces: DeviceInterfaces
        A back-reference to the collection of all interfaces; see Interfaces
        class definition.  This instance will be assigned when the actual
        interface is instantiated.  This back-reference will then provide access
        to the parent device.  See __repr__ for example usage.


    """

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
        self.sort_key = (self.name[0:2].lower(), *self.port_numbers)
        self._profile = None
        self.used = used
        self.desc = desc
        self.label = label
        self.profile = profile
        self.cable_peer: Optional[DeviceInterface] = None
        self.interfaces = interfaces

    # -------------------------------------------------------------------------
    #
    #                                Properties
    #
    # -------------------------------------------------------------------------

    @property
    def profile(self):
        """
        The `profile` property is used so that the interface instance can get
        assigned back into the profile so that there is a bi-directional
        relationship between the two objects.  This is necessary so references
        can be such that from a given profile -> interface -> device.

        Returns
        -------
        InterfaceProfile
        """
        return self._profile

    @profile.setter
    def profile(self, profile: "InterfaceProfile"):
        if not profile:
            self._profile = profile
            return

        if profile.interface:
            raise RuntimeError(
                f"Forbid to assign profile {profile.__class__.__class__} "
                f"to multiple interfaces: {self.device_ifname}"
            )

        self._profile = profile
        profile.interface = self

    @property
    def device(self):
        """
        The `device` allows the Caller to back reference the associated Device
        instance.  The device instance is bound to the device interfaces
        collection, such that: interface -> interfaces -> device.

        Returns
        -------
        Device
        """
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
