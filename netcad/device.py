# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Dict, Optional, TypeVar
from collections import defaultdict
from operator import attrgetter
from copy import deepcopy
from pathlib import Path

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device_interface import DeviceInterface
from netcad.helpers import Registry

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["Device", "DeviceInterface"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


PathLike = TypeVar("PathLike", str, Path)


class Device(Registry):
    """
    Device base class that is used by Caller to define specific Device useage
    representations, also referred to as "roles", "templates", 'stencils", etc.
    A Caller would then create multiple instances of the specific Device classes
    to declare muliple copies of the same role/etc.
    """

    # the `product_model` must exist in the SoT defined as-is.  For example, if
    # the product_model was "DCS-7050SX3-48YC12", then that device-model/type
    # must exist in the SoT.

    product_model: Optional[str] = None

    # The `interfaces` store the specific usage declaration for each of the
    # interfaces defined in the `product_model`.  All interfaces must be
    # declared, even if unused.

    interfaces: Dict[str, DeviceInterface] = None

    # The `template_file` stores the reference to the Jinja2 template file that
    # is used to render the specific device configuration.

    template_file: Optional[PathLike] = None

    def __init_subclass__(cls, **kwargs):
        """
        Upon Device sub-class definition create a unique set of interface
        definitions.  This step ensures that sub-classes do not *step on each
        other* when declaring interface definitions at the class level.  Each
        Device _instance_ will get a deepcopy of these interfaces so that they
        can make one-off adjustments to the device standard.
        """
        Registry.__init_subclass__()
        cls.interfaces = _DeviceInterfaces(DeviceInterface)
        cls.interfaces.device_cls = cls

    def __init__(self, name: str):
        self.name = name

        # make a copy of the device class interfaces so that the instance can
        # make any specific changes; i.e. handle the various "one-off" cases
        # that happen in real-world networks.

        self.interfaces = deepcopy(self.__class__.interfaces)
        self.interfaces.device = self
        self.registry_add(self.name, self)

    def get_source(self) -> str:
        """
        Returns the Jinja2 template source to render the device configuration.

        Returns
        -------
        """
        # TODO!
        pass

    def vlans(self):
        """return the set of VlanProfile instances used by this device"""

        vlans = set()

        # TODO: move this to a function; so that it can be called
        #       by the Jinja2 enviornment.

        # TODO: find all interfaces that are subclasses of InterfaceL2
        #       all L2 interfaces need to be subclassed from this.

        for if_name, iface in self.interfaces.items():
            if not (if_prof := getattr(iface, "profile", None)):
                continue

            if get_vlans := getattr(if_prof, "if_vlans", None):
                vlans.update(get_vlans())

        return sorted(vlans, key=attrgetter("vlan_id"))


class _DeviceInterfaces(defaultdict):
    """
    Private class definition that represents the collection of interfaces bound
    to a Device.
    """

    def __init__(self, default_factory, **kwargs):
        super(_DeviceInterfaces, self).__init__(default_factory, **kwargs)
        self.device_cls = None
        self.device = None

    def __missing__(self, key):
        # create a new instance of the device interface. add the back-reference
        # from the specific interface to this collection so that given any
        # specific interface instance, the Caller can reach back to find the
        # associated device object.
        iface = self[key] = DeviceInterface(name=key, interfaces=self)
        return iface
