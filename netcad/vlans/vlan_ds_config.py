# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, Field, Extra

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from .vlan_profile import VlanProfile

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["VlanDesignServiceConfig"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class VlanDesignServiceConfig(BaseModel, extra=Extra.forbid):
    """
    This class defines the available configuration options for the Vlans Design
    Service.  If a configuration is not provided by the Caller when the service
    is created then one will be automatically created with default values.
    """

    allow_unused_vlan1: bool = Field(
        default=True,
        description="Allow VLAN1 on devices even if not explicitly used in design",
    )

    default_vlan1: VlanProfile = Field(
        description="VLAN 1 profile if not provided by Caller",
        default_factory=lambda: VlanProfile(vlan_id=1),
    )
