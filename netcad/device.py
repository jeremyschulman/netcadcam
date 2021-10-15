# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Dict, Optional, TypeVar, List, TYPE_CHECKING
from collections import defaultdict
from operator import attrgetter
from copy import deepcopy
from pathlib import Path

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import jinja2

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device_interface import DeviceInterface
from netcad.interface_profile import InterfaceL2
from netcad.vlan_profile import SENTIAL_ALL_VLANS
from netcad.helpers import Registry

if TYPE_CHECKING:
    from vlan_profile import VlanProfile


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

    # The `template` stores the reference to the Jinja2 template file that
    # is used to render the specific device configuration.  If provided this
    # value is used by the `get_template` method.  If not provided, then the
    # Developer is expected to subclass Device and implement a `get_template`
    # method that returns the Template dynamically base on runtime values, such
    # as the device OS, model, etc.

    template: Optional[PathLike] = None

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

    def __init__(self, name: str, **kwargs):
        self.name = name

        # make a copy of the device class interfaces so that the instance can
        # make any specific changes; i.e. handle the various "one-off" cases
        # that happen in real-world networks.

        self.interfaces = deepcopy(self.__class__.interfaces)
        self.interfaces.device = self
        self.registry_add(self.name, self)

        # assign any User provided values
        for attr, value in kwargs.items():
            setattr(self, attr, value)

    def get_template(self, env: jinja2.Environment) -> jinja2.Template:
        """
        Return the absolute file-path to the device Jinja2 file.

        Returns
        -------
        str - as described.

        Raises
        ------
        RuntimeError:
            When the `template` value is not a str or Path.

        FileNotFoundError:
            When the template value is not a valid filesystem file.
        """
        if not self.template:
            raise RuntimeError(
                f"Missing template assignment: {self.__class__.__name__}"
            )

        if isinstance(self.template, str):
            as_path = Path(self.template)

        elif isinstance(self.template, Path):
            as_path = self.template

        else:
            raise RuntimeError(
                f"Unexpected template type on {self.__class__.__class__}: {type(self.template)}"
            )

        if not as_path.is_file():
            raise FileNotFoundError(
                f"Missing template {self.__class__.__name__}: {self.template}"
            )

        return env.get_template(str(as_path))

    def sorted_interfaces(self) -> List[DeviceInterface]:
        return sorted(
            self.interfaces.values(), key=lambda i: (i.name[0:2], *i.port_numbers)
        )

    def vlans(self) -> List["VlanProfile"]:
        """return the set of VlanProfile instances used by this device"""

        vlans = set()

        # TODO: move this to a function; so that it can be called
        #       by the Jinja2 enviornment.

        for if_name, iface in self.interfaces.items():
            if not (if_prof := getattr(iface, "profile", None)):
                continue

            if not isinstance(if_prof, InterfaceL2):
                continue

            used = if_prof.vlans_used()

            if SENTIAL_ALL_VLANS in used:
                used.remove(SENTIAL_ALL_VLANS)

            vlans.update(used)

        return sorted(vlans, key=attrgetter("vlan_id"))

    def __lt__(self, other):
        """
        For Device sortability purposes implement the less-than comparitor.  Subclasses
        can change this behavior for their own specific strategies.  A common one could
        follow a "chess-board" like (rank, file) value system.

        The default comparison will be based on the device name.
        """
        return self.name < other.name


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
