"""
This file provides the "VlansAll" descriptor that automates the process
of collecting all VlanProfiles defined on a given Device instance.

For details on Python Descriptors in general, see:
https://docs.python.org/3/howto/descriptor.html
"""

#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Union, Optional, Iterable, Set
from operator import attrgetter

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import DeviceInterface
from netcad.device.profiles.interface_profile import InterfaceProfile
from .vlan_profile import VlanProfile

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

    _assigned_attr_name: str
        The class attribute name that identifies where this descriptor is
        assigned to in the _assigned_cls.  Again used to determine whether or
        not to active the "skip-me" feature.
    """

    def __init__(
        self,
        include_vlans: Optional[Iterable[VlanProfile]] = None,
        exclude_vlans: Optional[Iterable[VlanProfile]] = None,
    ):
        self.include_vlans: Set[VlanProfile] = set(include_vlans or {})
        self.exclude_vlans: Set[VlanProfile] = set(exclude_vlans or {})

    def __set_name__(self, owner, name):
        if not issubclass(owner, InterfaceProfile):
            raise RuntimeError(
                f"Forbidden assignment of {self.__class__.__name__} to non InterfaceProfile class. "
                f"Attempted assignment to owner: {owner}, name: {name}"
            )

        self._skip_me = False
        self._assigned_attr_name = name

    def __get__(self, instance, objtype) -> Union["VlansAll", List[VlanProfile]]:
        """
        The "getter" is used to retrieve all vlans defined on the device.  The
        return value is a list of VlanProfile instances sorted by vlan_id.

        Parameters
        ----------
        instance:
            The instance, when not None, is the interface profile instance
            where the the attribute is assigned the VlansAll descriptor.

                For example, this class "UplinkSPtoTR" defines the attribute "vlans"
                and assigns the VlansAll descriptor.  The "instance" then is the
                specific instance of an UplinkSPtoTR class.

                    class UplinkSPtoTR(InterfaceL2Trunk):
                        desc = PeerInterfaceId()
                        native_vlan = fsl_vlans.vlan_transit_vpn
                        vlans = VlansAll()
                        template = Path("interface_trunk.jinja2")

            The instance, when None, is a call requesting the VlansAll
            descriptor instance itself.

        objtype:
            The class type for the instance.

        Returns
        -------
        A List of VlanProfile instances sorted by the vlan_id attribute.
        """

        # ---------------------------------------------------------------------
        # if no instance, then class lookup, return descriptor
        # ---------------------------------------------------------------------

        if instance is None:
            return self

        # ---------------------------------------------------------------------
        # need to iterate through all of the device interfaces and find all
        # VlanProfiles.  Need to avoid trying to getter on a profile that is
        # using the VlansAll descriptor to avoid recursion.
        # ---------------------------------------------------------------------

        this_iface: DeviceInterface = instance.interface
        this_device = this_iface.device
        dev_interfaces = this_device.interfaces

        collect_vlans = set()

        # set a flag on the interface profile instance
        instance._skip_me = True

        for if_name, iface in dev_interfaces.used().items():
            if getattr(iface.profile, "_skip_me", False) is True:
                continue

            # if the interface profile does not implement a `vlans_used` method
            # then we skip and move on.

            if not (vlans_used := getattr(iface.profile, "vlans_used", None)):
                continue

            vlans = vlans_used()

            # deactivate the skip-me since we've completed the call of
            # vlans_used which would be the source of any recursion.

            collect_vlans.update(vlans)

        # ----------------------------------------
        # return the collected set of VlanProfiles
        # ----------------------------------------

        instance._skip_me = False
        collect_vlans.update(self.include_vlans)
        collect_vlans -= self.exclude_vlans

        return sorted(collect_vlans, key=attrgetter("vlan_id"))
