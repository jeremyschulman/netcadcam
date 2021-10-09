# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, List, Type

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from jinja2 import Template

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.port_profile import PortProfile
from netcad.vlan_profile import VlanProfile

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


JinjaTemplateType = Type[Template]


class InterfaceProfile(object):

    # -------------------------------------------------------------------------
    # public Class attributes
    # -------------------------------------------------------------------------

    # `template` stores the Jinja2 template text that is used to render the
    # interface specicifc configuration text.

    template: Optional[str]

    # `port_profile` stores the physical layer information that is associated to
    # this interface.

    port_profile: Optional[PortProfile]

    # `desc` stores the interface description.  Set as a class value when all
    # instances share the same interface description value.

    desc: Optional[str]

    # -------------------------------------------------------------------------
    # private Class attributes
    # -------------------------------------------------------------------------

    # The `_template` stores the actula Jinja2 Template instance that will be
    # used/shared across multiple instances of the given profile.

    _template: Optional[Template]

    def __new__(cls, *args, **kwargs):
        """Used to instandiate just one copy of the shared jinja2 Template"""
        if cls.template and not hasattr(cls, "_template"):
            setattr(cls, "_template", Template(cls.template))

        return object.__new__(cls)

    def render(self, **kwargs) -> str:
        return self._template.render(**kwargs)


class InterfaceL2Access(InterfaceProfile):
    vlan: VlanProfile


class InterfaceL2Trunk(InterfaceProfile):
    native_vlan: Optional[VlanProfile]
    vlans: List[VlanProfile]
