#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Union, Dict
from pathlib import Path
from functools import cached_property

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import jinja2

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.phy_port.phy_port_profile import PhyPortProfile
from netcad.device.device_interface import DeviceInterface
from netcad.helpers import SafeIsAttribute

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "InterfaceProfile",
    "InterfaceVirtual",
]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class InterfaceProfile(SafeIsAttribute):
    # `template` stores the Jinja2 template text that is used to render the
    # interface specicifc configuration text.

    template: Optional[Union[str, Path]] = None

    # `port_profile` stores the physical layer information that is associated to
    # this interface.

    phy_profile: Optional[PhyPortProfile] = None

    # `desc` stores the interface description.  Set as a class value when all
    # instances share the same interface description value.

    desc: Optional[str] = ""

    def __init__(self, **kwargs):
        # the device instance this profile is bound to.  This value is assigned
        # by the DeviceInterface.profile propery

        self.interface: Optional[DeviceInterface] = None

        for attr, value in kwargs.items():
            setattr(self, attr, value)

    def get_template(self, env: jinja2.Environment) -> jinja2.Template:
        if not self.template:
            dev_name = self.interface.device.name
            if_name = self.interface.name
            raise RuntimeError(
                f"Interface {dev_name}:{if_name} profile missing template: {self.__class__.__name__}"
            )

        if isinstance(self.template, Path):
            return env.get_template(str(self.template))

        if isinstance(self.template, str):
            return env.from_string(self.template.lstrip())

        raise RuntimeError(
            "Interface profile unexpected template type: "
            f"{self.__class__.__name__}: {type(self.template)}"
        )

    @cached_property
    def profile_flags(self) -> Dict[str, bool]:
        flags = dict()
        for attr in filter(lambda i: i.startswith("is_"), dir(self)):
            attr_val = getattr(self, attr)
            if isinstance(attr_val, bool):
                flags[attr] = attr_val
        return flags

    @property
    def name(self):
        return self.__class__.__name__


class InterfaceVirtual(InterfaceProfile):
    """
    Mixin to denote that the interface is virtual / logical rather
    than a physical port.  Examples of virtual interfaces inlucde
    VLAN interfaces (SVIs) and Loopbacks.
    """

    is_virtual = True
