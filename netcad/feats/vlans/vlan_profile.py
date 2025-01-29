#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Hashable, TypeVar, Type

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import Field, model_validator

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.helpers import HashableModel

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["VlanProfile", "VlanProfileLike", "VlanProfileRegistry"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

VlanProfileRegistry: dict[str, "VlanProfile"] = dict()


class VlanProfile(HashableModel):
    """
    VlanProfile is used to store the specific attributes of a VLAN that is used
    by a network design.

    Attributes
    ----------
    name: str
        The VLAN name as it would be configured on the device

    vlan_id: int
        The VLAN number in the range [1..4094]

    description: str, optional
        Describes the purpose of the VLAN or other information.  Not all network
        devices support VLAN descriptions.  But the profile allows this
        attribute for (a) either those that do, (b) to add comments for those
        that do not, (c) netcad reporting information, or (d) helpful code docs.
    """

    name: Optional[str] = Field(
        None, description="VLAN name.  If not set then name is not checked"
    )
    vlan_id: int = Field(..., ge=1, le=4094)
    description: Optional[str] = Field(None)

    def __lt__(self, other: "VlanProfile"):
        """Enabled sorting by vlan-ID value"""
        return self.vlan_id < other.vlan_id

    @model_validator(mode="after")
    def _register(self):
        VlanProfileRegistry[self.name] = self
        return self


VlanProfileLike = TypeVar("VlanProfileLike", VlanProfile, Hashable)
VlanProfileType = Type[VlanProfile]
