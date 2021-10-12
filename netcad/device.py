# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Dict
from collections import defaultdict
from operator import attrgetter
from copy import deepcopy

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device_interface import DeviceInterface

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class Registry(object):
    __registry = None

    def __init_subclass__(cls, **kwargs):
        cls.__registry = dict()

    @classmethod
    def registry_add(cls, name, obj):
        cls.__registry[name] = obj

    @classmethod
    def registry_get(cls, name):
        return cls.__registry.get(name)


class DeviceInterfaces(defaultdict):
    def __init__(self, default_factory, **kwargs):
        super(DeviceInterfaces, self).__init__(default_factory, **kwargs)
        self.device_cls = None
        self.device = None

    def __missing__(self, key):
        self[key] = DeviceInterface(key)
        self[key].interfaces = self
        return self[key]


class Device(Registry):
    product_model = None
    template_file = None
    interfaces: Dict[str, DeviceInterface] = None

    def __init_subclass__(cls, **kwargs):
        """
        Upon Device sub-class definition we a unique set of interface
        definitions.  This step ensures that sub-classes do not *step on each
        other* when declaring interface definitions at the class level.  Each
        Device _instance_ will get a deepcopy of these interfaces so that they
        can make one-off adjustments to the device standard.
        """
        Registry.__init_subclass__()
        cls.interfaces = DeviceInterfaces(DeviceInterface)
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

        for if_name, iface in self.interfaces.items():
            if not (if_prof := getattr(iface, "profile", None)):
                continue

            if get_vlans := getattr(if_prof, "if_vlans", None):
                vlans.update(get_vlans())

        return sorted(vlans, key=attrgetter("vlan_id"))
