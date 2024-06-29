#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, TypeVar, List, Type, Dict
from typing import TYPE_CHECKING
import os
from copy import deepcopy
from pathlib import Path
from itertools import chain
from ipaddress import IPv4Interface, IPv6Interface, ip_interface

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import jinja2

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.registry import Registry
from netcad.config import Environment
from netcad.config import netcad_globals
from netcad.jinja2.j2_env import get_env, expand_templates_dirs
from netcad.notepad import Notepad

from .device_type import DeviceType, DeviceTypeRegistry
from .device_interfaces import DeviceInterfaces
from .device_interface import DeviceInterface
from .profiles import InterfaceL3
from .device_interface_parse_name import (
    DeviceInterfaceNameParsed,
    default_interface_parse_name,
)
from .interface_ip import InterfaceIP, to_interface_ip

if TYPE_CHECKING:
    from netcad.design import Design, DesignFeatureCatalog, DesignFeatureLike


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["Device", "DeviceInterface", "DeviceCatalog", "DeviceKindRegistry"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


PathLike = TypeVar("PathLike", str, Path)

DeviceKindRegistry: dict[str, "DeviceType"] = dict()


class Device(Registry, registry_name="devices"):
    """
    Device base class that is used by Caller to define specific Device useage
    representations, also referred to as "roles", "templates", 'stencils", etc.
    A Caller would then create multiple instances of the specific Device classes
    to declare muliple copies of the same role/etc.

    Attributes
    ----------
    os_name: str, required
        Unqiue indentifies the device operating system name.  Arista, for
        example, this value would likely be "eos".  The Designer can use any
        values they choose (i.e. does not need to be eos for Arista), but they
        must use names that are unqiue within their SOT.

    device_type: str, optional
        When used, this value selects the device type definition from the origin
        that provides the device-type specification. Must exist in the source of
        truth (SoT) defined as-is.  For example, if the product_model was
        "DCS-7050SX3-48YC12", then that device-model/type must exist in the SOT.

    product_model: str, required
        The device product model value as expected to be reported from the
        device; for example from a "show version" command.  This value will also
        be used as the default `device_type` for obtaining device-type
        specifications.  If the product_model and the device specification value
        need to be different, then use the optional `device_type` value.

    interfaces: dict[str, DeviceInterface]
        Store the specific usage declaration for each of the interfaces defined
        in the `product_model`.  All interfaces must be declared, even if
        unused.

    template: PathLike
        The `template` stores the reference to the Jinja2 template file that is
        used to render the specific device configuration.  If provided this
        value is used by the `get_template` method.  If not provided, then the
        Developer is expected to subclass Device and implement a `get_template`
        method that returns the Template dynamically base on runtime values,
        such as the device OS, model, etc.
    """

    os_name: Optional[str] = None

    device_type: Optional[str] = None

    product_model: Optional[str] = None

    device_type_sepc: Optional[DeviceType] = None

    interfaces: DeviceInterfaces = None
    interfaces_map: Dict[str, str] = dict()

    template: Optional[PathLike] = None

    def __init__(
        self,
        name: str,
        alias: str | None = None,
        primary_ip: str | None = None,
        **kwargs,
    ):
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

        self.alias = alias or name
        self.name = name
        self.sort_key = name

        self._primary_ip: Optional[IPv4Interface | IPv6Interface] = primary_ip
        self._primary_ip_interface: Optional[DeviceInterface] = None

        # make a copy of the device class interfaces so that the instance can
        # make any specific changes; i.e. handle the various "one-off" cases
        # that happen in real-world networks.

        self.interfaces: DeviceInterfaces = deepcopy(self.__class__.interfaces)

        # TODO: not sure why the device_cls attribute was not copied as part of
        #       the deepcopy above; need to investigate.  But for now, put the
        #       value back into the interfaces

        self.interfaces.device_cls = self.__class__

        # create the back-references from the interfaces instance to this
        # device.

        self.interfaces.device = self

        # register this device hostname to the subclass.

        self.registry_add(self.name, self)

        # A device is "owned" by a Design instance.  Need to keep a
        # back-reference to this design instance since it will be used to back
        # reference other related design elements by the device through the
        # Developer specific usage.

        self.design: Optional["Design"] = None

        # features is a list of DesignFeature instances bound to this device.
        # These features will later be used to generate test cases.

        self.features: DesignFeatureCatalog = dict()

        # for any Caller provided values, override the class attributes; or set
        # new attributes (TODO: rethink this approach)

        for attr, value in kwargs.items():
            setattr(self, attr, value)

        self.template_env: Optional[jinja2.Environment] = None
        self.notepad = Notepad(owner=self)

    @classmethod
    def parse_interface_name(cls, name: str) -> DeviceInterfaceNameParsed:
        return default_interface_parse_name(name)

    def set_primary_ip_interface(self, interface: DeviceInterface) -> "Device":
        """
        This function is used to assign the device primary IP address using the
        provided device interface.  The device interface is then associated as
        an attribute to the IP instance so that the "back-reference" exists
        when needed.  This use is common for example, in Jinja2 templating that
        looks like this:

        ip tacacs source-interface {{ device.primary_ip.interface.name }}

        Parameters
        ----------
        interface: DeviceInterface
            Must have an InterfaceL3 based profile assigned, and that must have
            an if_ipaddr value assigned.

        Returns
        -------
        Device self instance for use with method-chanining.
        """
        if not interface.profile:
            raise ValueError(
                f"Device {self.name} interface {interface.name} does not have profile assigned."
            )

        if not isinstance(interface.profile, InterfaceL3):
            raise ValueError(
                f"Device {self.name} interface {interface.name} is not a L3 profile"
            )

        if not (if_ipaddr := interface.profile.if_ipaddr):
            raise ValueError(
                f"Device {self.name} interface {interface.name} does not have profile assigned."
            )

        self._primary_ip = if_ipaddr
        self._primary_ip_interface = interface

        # for method-chaining
        return self

    @property
    def primary_ip(self) -> InterfaceIP | None:
        """
        Returns an InterfaceIP instance that is the ip_address instance for the
        device primary IP address, augmented with an 'interface' attribute. The
        interface attribute is the DeviceInterface instance hosting the primary
        IP address.

        Notes
        -----
        Supports both IPv4 and IPv6 use-cases

        Returns
        -------
        The InterfaceIP instance for the primary IP, if assigned.  None
        otherwise.
        """
        try:
            return to_interface_ip(
                ip=self._primary_ip.ip, interface=self._primary_ip_interface
            )
        except AttributeError:
            return None

    @primary_ip.setter
    def primary_ip(self, ipaddr: str):
        self.set_primary_ip(ip_interface(ipaddr))

    def set_primary_ip(self, ipaddr: str):
        raise NotImplementedError()

    def services_of(
        self, svc_cls: Type["DesignFeatureLike"]
    ) -> List["DesignFeatureLike"]:
        """Return the device features that are of the given service type"""
        return [svc for svc in self.features.values() if isinstance(svc, svc_cls)]

    # -------------------------------------------------------------------------
    #
    #                  Config Template Building Related
    #
    # -------------------------------------------------------------------------

    def init_template_env(self, templates_dir: Optional[Path] = None):
        template_dirs = []
        if not (template_decls := netcad_globals.g_config.get("templates")):
            top_tdir = templates_dir or netcad_globals.g_netcad_templates_dir
            top_os_tdir = top_tdir.joinpath(self.os_name)
            template_dirs.append(top_os_tdir)
            template_dirs.append(top_tdir)
        else:
            paths = chain.from_iterable(d["paths"] for d in template_decls)
            paths = expand_templates_dirs(paths=paths, obj=self)
            template_dirs.extend(paths)

        template_dirs.append("/")
        self.template_env = get_env(template_dirs)

    def render_config(self, template_file: Optional[Path | str] = None):
        template = self.get_template(template_file)
        return template.render(device=self)

    def get_template(
        self, template_file: Optional[Path | str] = None
    ) -> jinja2.Template:
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
        _use_template = template_file or self.template

        if not _use_template:
            raise RuntimeError(
                f"Missing template assignment: {self.__class__.__name__}"
            )

        if isinstance(_use_template, str):
            as_path = Path(_use_template)

        elif isinstance(_use_template, Path):
            as_path = _use_template

        else:
            raise RuntimeError(
                f"Unexpected template type on {self.__class__.__class__}: {type(_use_template)}"
            )

        return self.template_env.get_template(str(as_path))

    def get_interfaces_notes(self) -> list:
        return [
            _notes
            for if_obj in self.interfaces.values()
            if (_notes := if_obj.get_notes())
        ]

    # -------------------------------------------------------------------------
    #
    #                            Class Methods
    #
    # -------------------------------------------------------------------------

    def __init_subclass__(cls, **kwargs):
        """
        Upon Device subclass definition create a unique set of interface
        definitions.  This step ensures that subclasses do not *step on each
        other* when declaring interface definitions at the class level.  Each
        Device _instance_ will get a deepcopy of these interfaces so that they
        can make one-off adjustments to the device standard.
        """

        super().__init_subclass__(**kwargs)
        DeviceKindRegistry[cls.__name__] = cls

        cls.interfaces = DeviceInterfaces(DeviceInterface)
        cls.interfaces.device_cls = cls

        # when the Device class defines either product_model or device_type,
        # configure the state of the interfaces; persuming the "no-validate"
        # ENV is not set.

        if (
            getattr(cls, "product_model", None) or getattr(cls, "device_type", None)
        ) and not os.getenv(Environment.NETCAD_NOVALIDATE):
            cls.init_device_spec()

    @classmethod
    def init_device_spec(cls):
        """
        Called from __init_subclass__, this function is used to retrieve the
        device-type specification using the designated product-model.

        A subclass could override this method to perform any specific further
        device-product design initialization or validation.
        """

        device_type = cls.device_type or cls.product_model

        cls.device_type_spec: DeviceType = DeviceTypeRegistry.registry_get(
            name=device_type
        )

        if not cls.device_type_spec:
            raise RuntimeError(
                f"Device class {cls.__name__} missing spec for device-type: {device_type}.  "
            )

        # if the device_type was specified, then autopopulate the
        # product_model based on the device_type_spec.

        if not cls.product_model:
            cls.product_model = cls.device_type_spec.product_model

        # # initialize the interfaces in the device so that those defined in the
        # # spec exist; initializing the profile value to None.

        for if_name in cls.device_type_spec.interfaces:
            cls.interfaces[if_name].profile = None

    # -------------------------------------------------------------------------
    #
    #                           Dunder methods
    #
    # -------------------------------------------------------------------------

    def __getattr__(self, item):
        """
        Implement a mechanism that allows a Caller to check for the existance of
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

    def __lt__(self, other: "Device"):
        """
        For Device sortability purposes implement the less-than comparitor.  Subclasses
        can change this behavior for their own specific strategies.  A common one could
        follow a "chess-board" like (rank, file) value system.

        The default comparison will be based on the device name.
        """
        try:
            return self.sort_key < other.sort_key
        except TypeError as exc:
            raise RuntimeError(
                "Device sort-key type mismatch between "
                f"{self.name}:{type(self)} and {other.name}:{type(other)}\n"
                f"{str(exc)}"
            )

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"


# A device catalog is a dictionary of devices key=dev.name, value=device-obj
DeviceType = Type[Device]
DeviceCatalog = Dict[str, Device]
