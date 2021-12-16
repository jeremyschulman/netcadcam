# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import Field

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.helpers import HashableModel

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "VlanProfile",
]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

# noinspection PyUnresolvedReferences
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

    name: str
    vlan_id: int = Field(..., ge=1, le=4094)
    description: Optional[str]

    def __lt__(self, other: "VlanProfile"):
        """Enabled sorting by vlan-ID value"""
        return self.vlan_id < other.vlan_id
