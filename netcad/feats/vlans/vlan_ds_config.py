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

    check_vlan1: bool = Field(
        default=False,
        description="Check design for VLAN1",
    )

    default_vlan1: VlanProfile = Field(
        description="VLAN1 profile if not provided by Caller",
        default_factory=lambda: VlanProfile(vlan_id=1),
    )
