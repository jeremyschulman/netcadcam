#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Union, Iterable, List, Callable
from typing import TYPE_CHECKING
import re

if TYPE_CHECKING:
    from netcad.device.profiles import InterfaceProfile

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import jinja2

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
_re_find_words = re.compile(r"\b([a-z]+)\b", re.IGNORECASE)

# short-name is the first two characters of the name, followed by the remaining
# interface numbers.  For example, "Ethernet49/1" turns into "Et49/1"

_re_short_name = re.compile(r"(\D\D)\D+(\d.*)")


# noinspection PyUnresolvedReferences
class DeviceInterface(object):
    """
    DeviceInterface models the properties of a network device interface as it is
    used in a design.  A DeviceInterface exists for each interface in the
    device-type specification.  For example "Ethernet1" is an interface name for
    a DeviceInterface.  "Port-Channel5" could also be a DeviceInterface, even
    though it is not a physical interface.

    Attributes
    ----------
    name : str
        The full-name of the interface, for example "Ethernet49/1"

    short_name: str
        A shortened version of the full-name that is composed of only the first
        two letters, followed by the numberical portion. An interface name
        "Ethernet50/1" would have a short_name "Et50/1".

    port_numbers: Tuple[Int]
        A tuple of only the numbers in the interface name. These are useful for
        numerical sorting purpose. An interface with name "GigabitEtherent1/0/2"
        would have port_numbers = (1,0,2).

    sort_key: Tuple[str, int, ...]
        A tuple that can be used for sorting a list of interfaces.  The first
        value in the tuple is the first two characters of the name.  The
        remaning values are the port_numbers.  An interface name "Ethernet49"
        would have a sort_key ("et", 49), for example.

    cable_id: str
        A name that unqiuely identifies a cable within a cabling plan.  The
        cabling plan will "match-up" interfaces that have the same cable_id to
        create both physical and logical "cable_peer" relationships.

    cable_peer: DeviceInterface
        The instance of the device-interface on the far end of a cable
        relationship.

    cable_port_id : str
        The `cable_port_id` attribute is used to return the value which would
        show up as the "port-id" in LLDP or CDP cabling tests.  By default, the
        cable_port_id is the interface name.  A Designer may wish to override
        this default behavior by seeting the cable_port_it property value.

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
        enabled: Optional[bool] = False,  # interfaces are disabled by deafult
        desc: Optional[str] = "",
        cable_id: Optional[str] = None,
        label: Optional[str] = None,
        interfaces=None,
    ):
        self.name = name

        # need the device class, so we know how to parse the interface names.

        device_cls = interfaces.device_cls
        ifn_parsed = device_cls.parse_interface_name(name)

        self.short_name = ifn_parsed.short_name
        self.sort_key = ifn_parsed.sort_key
        self.port_numbers = ifn_parsed.numbers

        self._profile = None
        self._desc = desc
        self.enabled = enabled
        self.label = label
        self.cable_id = cable_id

        # hold the Designer defined cable_port_id override value.
        self._cable_port_id = None

        self.profile = profile
        self.cable_peer: Optional[DeviceInterface] = None
        self.interfaces = interfaces

    # -------------------------------------------------------------------------
    #
    #                          Properties Read-Only
    #
    # -------------------------------------------------------------------------

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
    def cable_port_id(self) -> str:
        """
        Returns the value of this interface "port-id" as it would be seen from
        the LLDP neighbor data.  Typically, this is the same as the inteface
        name. There are circumstances, however, where this is not the case.
        """
        return (
            self._cable_port_id(self)
            if callable(self._cable_port_id)
            else (self._cable_port_id or self.name)
        )

    @cable_port_id.setter
    def cable_port_id(self, value: Union[Callable, str]):
        self._cable_port_id = value

    @property
    def used(self):
        """An interface is used by the design if it has an assigned profile."""
        return bool(self.profile)

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
            case since a device will automatically be assigned during the
            defaultdict process of the Device object.  Added this raise for
            dev-testing purposes.
        """
        parent = self.interfaces
        ifn_lc = self.short_name.lower()
        device_name = (
            parent.device.name if parent.device else parent.device_cls.__name__
        )
        return f"{device_name}-{ifn_lc}"

    # -------------------------------------------------------------------------
    #
    #                          Properties Read-Write
    #
    # -------------------------------------------------------------------------

    @property
    def desc(self) -> str:
        return self._desc or (self.profile.desc if self.profile else "")

    @desc.setter
    def desc(self, value):
        self._desc = value

    @property
    def profile(self) -> "InterfaceProfile":
        """
        The `profile` property is used so that the interface instance can get
        assigned back into the profile so that there is a bidirectional
        relationship between the two objects.  This is necessary so references
        can be such that from a given profile -> interface -> device.

        Returns
        -------
        InterfaceProfile
        """
        return self._profile

    @profile.setter
    def profile(self, profile: "InterfaceProfile"):

        # when a profile is set to None, then the interface.enabled is set to

        if not profile:
            self._profile = None
            self.enabled = False
            return

        if profile.interface:
            raise RuntimeError(
                f"Forbid to assign profile {profile.__class__.__name__} "
                f"to multiple interfaces: {self.device_ifname}"
            )

        # when a profile is assigned to an interface, then the enabled attribute
        # is set to True by default.  A Designer could then set .enabled=False
        # to indicate that the interface should be configured to be
        # admin-disabled; but keep the profile so that the interface config
        # rendering still is peformed.

        self._profile = profile
        self.enabled = True

        profile.interface = self

    @staticmethod
    def sorted_interface_names(if_names: Iterable[str]) -> List[str]:
        """
        This helper function is used to return a sorted list of interface names
        (strings).  The input `if_names` can be any iterable collection
        providing the source interface names.

        Parameters
        ----------
        if_names

        Returns
        -------
        List of sorted interface names.
        """
        return [iface.name for iface in sorted(map(DeviceInterface, if_names))]

    # -------------------------------------------------------------------------
    #
    #                     Supporting Jinja2 Config Building
    #
    # -------------------------------------------------------------------------

    @jinja2.pass_context
    def render(self, ctx: jinja2.runtime.Context) -> str:
        """
        Used to create the interface specific configuration text based on the
        associated interface profile.  If the interface is "not used", then the
        parent device will provide a profile via the "unused_interface_profile"
        Attribute

        Parameters
        ----------
        ctx: Jinja2 context
            This provides the running Jinja2 environment since this method is
            executed during the course of creating the device configuration.

        Returns
        -------
        str as described
        """

        profile = self.profile or self.device.unused_interface_profile

        return (
            profile.get_template(ctx.environment)
            .render(device=self.device, interface=self)
            .rstrip()
        )

    # -------------------------------------------------------------------------
    #
    #                               Dunder Overrides
    #
    # -------------------------------------------------------------------------

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

    def __lt__(self, other: "DeviceInterface"):
        return self.sort_key < other.sort_key

    # -------------------------------------------------------------------------
    # Context manager to "self" to allow for multiple attribute assignments so
    # that Caller can do something like:
    #
    #    with device.interfaces['Ethernet1'] as iface:
    #       iface.profile = ...
    #       iface.cable_id = ...
    #
    # -------------------------------------------------------------------------

    def __enter__(self) -> "DeviceInterface":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
