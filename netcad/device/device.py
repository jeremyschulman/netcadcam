# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Dict, Optional, TypeVar, List, TYPE_CHECKING, Set
import os
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

from netcad.device.device_interface import DeviceInterfaces, DeviceInterface
from netcad.registry import Registry
from netcad.config.cache import cache_load_device_type
from netcad.config import Environment

if TYPE_CHECKING:
    from netcad.vlan.vlan_profile import VlanProfile


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
DeviceInterfacesLike = TypeVar("DeviceInterfacesLike", DeviceInterfaces, dict)


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

    def __init__(self, name: str, **kwargs):
        """
        Device initialization creates a specific device instance for the given
        subclass.

        Parameters
        ----------
        name: str
            The device hostname value.

        Other Parameters
        ----------------
        key-values that override the class attributes.
        """

        self.name = name

        # make a copy of the device class interfaces so that the instance can
        # make any specific changes; i.e. handle the various "one-off" cases
        # that happen in real-world networks.

        self.interfaces: DeviceInterfacesLike = deepcopy(self.__class__.interfaces)

        # create the back-references from the interfaces instance to this
        # device.

        self.interfaces.device = self

        # register this device hostname to the subclass.

        self.registry_add(self.name, self)

        # for any Caller provided values, override the class attributes; or set
        # new attributes (TODO: rethink this approach)

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
        """
        Returns a list of interface instances sorted using a
        Returns
        -------

        """
        # TODO: change this to sorted(self.interfaces) and test.
        return sorted(
            self.interfaces.values(), key=lambda i: (i.name[0:2], *i.port_numbers)
        )

    def vlans(self) -> List["VlanProfile"]:
        """return the set of VlanProfile instances used by this device"""

        all_vlans: Set[VlanProfile] = set()

        for if_name, iface in self.interfaces.items():
            if not iface.profile:
                continue

            if not (vlans_used := getattr(iface.profile, "vlans_used", None)):
                continue

            all_vlans.update(vlans_used())

        return sorted(all_vlans, key=attrgetter("vlan_id"))

    # noinspection PyMethodMayBeStatic
    def testing_services(self) -> List[str]:
        """
        This function returs the list of TestCases service names that will be
        used for creating the device's network state audits.  The Device base
        class will always return the following (and showing their associated
        TestCases class for reference).

           * "interfaces" -> InterfaceTeestCases
           * "vlans" -> VlanTestCases
           * "lags" -> LagTestCases

        Returns
        -------
        List[str] as described.
        """
        return ["interfaces", "vlans", "lags"]

    # -------------------------------------------------------------------------
    #
    #                            Class Methods
    #
    # -------------------------------------------------------------------------

    def __init_subclass__(cls, **kwargs):
        """
        Upon Device sub-class definition create a unique set of interface
        definitions.  This step ensures that sub-classes do not *step on each
        other* when declaring interface definitions at the class level.  Each
        Device _instance_ will get a deepcopy of these interfaces so that they
        can make one-off adjustments to the device standard.
        """
        Registry.__init_subclass__()
        cls.interfaces = DeviceInterfaces(DeviceInterface)
        cls.interfaces.device_cls = cls

        # configure the state of the interfaces by default to unused. this
        # settings will be determined by the `init_interfaces()` class method.
        # By default, will set interfaces to unused. This behavior could be
        # changed by the sublcass.

        if getattr(cls, "product_model", None) and not os.getenv(
            Environment.NETCAD_NOVALIDATE
        ):
            cls.init_interfaces()

    @classmethod
    def init_interfaces(cls):
        """
        Called from __init_subclass__, this function is used to retrieve the
        device-type specification using the designated product-model.

        A subclass could override this method to perform any specific further
        device-product design initialization or validation.
        """

        try:
            spec = cls.device_type_spec = cache_load_device_type(
                product_model=cls.product_model
            )
        except FileNotFoundError:
            raise RuntimeError(
                f"Missing device-type file for {cls.__name__}, product-model: {cls.product_model}.  "
                'Try running "netcad get device-types" to fetch definitions.'
            )

        # initialize the interfaces in the device so that those defined in the
        # spec exist; initializing the profile value to None.

        for if_def in spec["interfaces"]:
            cls.interfaces[if_def["name"]].profile = None

    # -------------------------------------------------------------------------
    #
    #                           Dunder methods
    #
    # -------------------------------------------------------------------------

    def __getattr__(self, item):
        """
        Impement a mechanism that allows a Caller to check for the existance of
        an attribute that has the form "is_xxxx".  For example:

            if device.is_pseudo:
                ...

        Would safely check if the device instance has the attribute. This
        mechanism allows for a syntatic sugar usage so that the caller does not
        need to do hasattr(device, "is_pseudo").

        Parameters
        ----------
        item: str
            The attribute name the Caller is referencing.

        Returns
        -------
        bool - True when the instance has the attribute, False otherwise
        """

        if item.startswith("is_"):
            return False

        raise AttributeError(item)

    def __lt__(self, other):
        """
        For Device sortability purposes implement the less-than comparitor.  Subclasses
        can change this behavior for their own specific strategies.  A common one could
        follow a "chess-board" like (rank, file) value system.

        The default comparison will be based on the device name.
        """
        return self.name < other.name
