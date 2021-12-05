# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Set
from operator import attrgetter

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device.interface_profile import InterfaceProfile
from netcad.vlan import VlanProfile

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["VlansAll"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class VlansAll:
    """
    VlansAll is a descriptor that can be assigned to a InterfaceProfile class
    attribute.  The common use is on the InterfaceL2Trunk.vlans attribute when
    the interface is an uplink port from one device to another with the
    expectation to carry all the vlans between the two.

    The getter returns a list of VlanProfiles used by the device; i.e. across
    all the interfaces that have associated L2 interface profiiles.

    Attributes
    ----------
    _skip_me: bool
        Used to thwart recursion when the descriptor getter is called during
        code execution that referrs back to the attribute.  This process happens
        by the any InterfaceProfile that implements the used_vlans() method to
        include return the list of VlanProfiles defined by that attribute.  But
        that attribute could be using this descriptor!  Initially the _skip_me
        is set to False.  It is set to True when the descritor getter is invoked
        and detected in use by the instance.attribute for it was bound to during
        the __set_name__ call.

    _assigned_cls: type
        The class type for which this descriptor is bound to.  This is used to
        determine during getter whether or not to active the "skip-me" feature.

    _assigned_attr_name: str
        The class attribute name that identifies where this descriptor is
        assigned to in the _assigned_cls.  Again used to determine whether or
        not to active the "skip-me" feature.
    """

    def __set_name__(self, owner, name):
        if not issubclass(owner, InterfaceProfile):
            raise RuntimeError(
                f"Forbidden assignment of {self.__class__.__name__} to non InterfaceProfile class. "
                f"Attempted assignment to owner: {owner}, name: {name}"
            )

        self._skip_me = False
        self._assigned_cls = owner
        self._assigned_attr_name = name

    def __get__(self, instance, owner):

        # if no instance, then class lookup, return descriptor
        if instance is None:
            return self

        # need to iterate through all of the device interfaces and find all
        # VlanProfiles.  Need to avoid trying to getter on a profile that is
        # using the VlansAll descriptor to avoid recursion.

        all_vlans: Set[VlanProfile] = set()
        dev_interfaces = instance.interface.device.interfaces

        for if_name, iface in dev_interfaces.items():

            # if the skip-me feature is activated it means that this descriptor
            # is already in the execution call stack, so we need to avoid
            # recursion.  Also if there is no profile assigned to this interface
            # then we skip it.

            if self._skip_me or not iface.profile:
                continue

            # if the interface profile does not implement a `vlans_used` method
            # then we skip and move on.

            if not (vlans_used := getattr(iface.profile, "vlans_used", None)):
                continue

            # if this interface.attribute is assigned the VlansAll descriptor
            # itself, then we need to mark this descriptor as being in the
            # execution call stack and to "skip" it should the
            # inteface.attribute be called again during the invokation of the
            # `vlans_used` method.

            if isinstance(iface.profile, self._assigned_cls) and isinstance(
                getattr(iface.profile.__class__, self._assigned_attr_name), VlansAll
            ):
                self._skip_me = True

            # invoke the vlans_used method that will return a list of
            # VlanProfiles assigned on this interface.

            vlans = vlans_used()

            # deactivate the skip-me since we've completed the call of
            # vlans_used which would be the source of any recursion.

            self._skip_me = False

            all_vlans.update(vlans)

        # return a list of VlanProfiles sorted by the vlan_id attribute.  That
        # is in VLAN ID numerical order low to high.

        return sorted(all_vlans, key=attrgetter("vlan_id"))
