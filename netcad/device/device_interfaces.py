#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Dict, DefaultDict
from collections import defaultdict

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .device_interface import DeviceInterface

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["DeviceInterfaces"]

# -----------------------------------------------------------------------------
#
#                    DeviceInterfaces Collection
#
# -----------------------------------------------------------------------------


class DeviceInterfaces(defaultdict, DefaultDict[str, "DeviceInterface"]):
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
    ) -> Dict[str, "DeviceInterface"]:
        """
        Return dictionary that allows the Caller to iterate over each of the
        device interfaces for those that are in use.  The term "used" means
        that the interface is used in the design, but does not necessarily mean
        that the interface is designed to be up.  By default, the "disabled"
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

    def unused(self) -> Dict[str, "DeviceInterface"]:
        """
        Returns a dictiionary of the unused interfaces.
        """
        return dict(
            (if_name, if_obj) for if_name, if_obj in self.items() if not if_obj.used
        )

    def startswith(self, prefix, used=None):
        for if_name, iface in self.items():
            if not if_name.startswith(prefix):
                continue

            # if used is "don't care" then yield
            if used is None:
                yield iface

            # if both used and iface.used are the same
            elif used == iface.used:
                yield iface
