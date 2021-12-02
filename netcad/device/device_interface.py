# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Dict, DefaultDict, Iterable, List
from typing import TYPE_CHECKING
from io import StringIO
import re
from collections import defaultdict

if TYPE_CHECKING:
    from netcad.device.interface_profile import InterfaceProfile

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import jinja2

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["DeviceInterface", "DeviceInterfaces"]

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

        # some device ports are just numbers.  In these instances set the
        # interface attributes accordinly.

        if name.isdigit():
            self.port_numbers = int(name)
            self.sort_key = self.port_numbers
            self.short_name = name

        # if the name contains numbers then break these numbers out for
        # sorting purposes.

        elif mo_has_numbers := _re_find_numbers.findall(name):
            self.port_numbers = tuple(map(int, mo_has_numbers))
            self.short_name = "".join(_re_short_name.match(name).groups())
            self.sort_key = (self.name[0:2].lower(), *self.port_numbers)

        # the name is not a number nor does it contain numbers, for example "mgmt",
        # then set the number value to 0 for default purposes.
        else:
            self.short_name = name
            self.sort_key = 0
            self.port_numbers = None

        self._profile = None
        self._desc = desc
        self.enabled = enabled
        self.label = label
        self.cable_id = cable_id
        self.profile = profile
        self.cable_peer: Optional[DeviceInterface] = None
        self.interfaces = interfaces

    # -------------------------------------------------------------------------
    #
    #                          Properties Read-Only
    #
    # -------------------------------------------------------------------------

    @property
    def used(self):
        """An interface is used by the design if it has an assigned profile."""
        return bool(self.profile)

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

    # -------------------------------------------------------------------------
    #
    #                          Properties Read-Write
    #
    # -------------------------------------------------------------------------

    @property
    def desc(self):
        return self._desc or (self.profile.desc if self.profile else None)

    @desc.setter
    def desc(self, value):
        self._desc = value

    @property
    def profile(self) -> "InterfaceProfile":
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

    def __enter__(self) -> "DeviceInterface":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# -----------------------------------------------------------------------------
#
#                    DeviceInterfaces Collection
#
# -----------------------------------------------------------------------------


class DeviceInterfaces(defaultdict, DefaultDict[str, DeviceInterface]):
    """
    The collection of interfaces bound to a Device.  Subclasses a defaultdict so
    that the Caller can create ad-hoc interfaces that are not originally part of
    the device-type specification.

    Ad-hoc, for example, could be Port-Channel interfaces or Vlan interfaces
    (SVI).
    """

    def __init__(self, default_factory, **kwargs):
        super(DeviceInterfaces, self).__init__(default_factory, **kwargs)
        self.device_cls: Optional[DeviceInterface] = None
        self.device = None

    def __missing__(self, key):
        # create a new instance of the device interface. add the back-reference
        # from the specific interface to this collection so that given any
        # specific interface instance, the Caller can reach back to find the
        # associated device object.

        self[key] = DeviceInterface(name=key, interfaces=self)
        return self[key]

    def used(
        self, include_disabled=True, include_unused=False
    ) -> Dict[str, DeviceInterface]:
        """
        Return dictionary that allows the Caller to iterate over each of the
        device interfaces for those that are in use.  The term "used" means that
        the interface is used in the design, but does not necessarily mean that
        the interface is designed to be up.  By default the "disabled"
        interfaces WILL be included in the returned dictionary.  If the Caller
        does not want the disabled interfaces, then set the `include_disabled`
        param to False.

        Parameters
        ----------
        include_disabled: bool, optional(default=True)
            When False the function will not include any interfaces that are
            disabled, even though used, in the design.

        include_unused: bool, optional(default=False)
            When True the function will include an interface even though it is
            not used in a design.  For example, if a management port is not used
            in the design, but the Caller does want to include it for some
            reason, then they would set this parameter to True.

        Returns
        -------
        dict
        """
        used_interfaces = dict()

        interface: DeviceInterface
        for if_name, interface in self.items():

            # if there is no profile bound to the interface, then it is not part
            # of the design; so skip it unless the caller wants to include disabled

            if not interface.profile and include_unused is False:
                continue

            # if the interface is in the design, but the design indicates to
            # disable ("shutdown") the interface, then by default include it in
            # the return.  If the Caller set `include_disabled` to False then
            # skip it.

            if interface.enabled is False and include_disabled is False:
                continue

            used_interfaces[if_name] = interface

        return used_interfaces

    def render(self, ctx: jinja2.runtime.Context, prefix: Optional[str] = None):
        env = ctx.environment
        content = StringIO()

        device = self.device

        # we want the interfaces output in numerical order, so sort the
        # collection using the designated interface port numbers (tuple). we
        # also want the sort to be based on the prefix of the first two
        # characters of the interface name, so that "Ethernet1" comes before
        # "Management1", for exmaple.

        interfaces = sorted(self.values())
        if prefix:
            interfaces = sorted(
                iface for iface in interfaces if iface.name.startswith(prefix)
            )

        for interface in interfaces:

            # if the interface is not used at all, then use the "unused
            # interface" template, and then done processing this interface into
            # the config build process.

            if not interface.used:
                if_content = device.render_interface_unused(
                    env=env, interface=interface
                )

            # if the interface is used, then it MUST have an assigned profile.
            # If it does not, then raise an exception.

            elif not interface.profile:
                raise RuntimeError(
                    f"Unexpected missing interface profile on: {interface.name}"
                )

            else:
                if_content = device.render_interface_used(env=env, interface=interface)

            content.write(if_content)

        # rewind the IO buffer and return back everything except the final
        # newline since that will be added by the in template including this
        # render.

        content.seek(0)
        as_str = content.read()
        return as_str[:-1]
