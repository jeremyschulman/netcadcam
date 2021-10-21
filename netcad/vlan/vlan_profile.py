# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic.dataclasses import Field

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.helpers import HashableModel

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["VlanProfile"]


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
    description: Optional[str] = Field(None)


# -----------------------------------------------------------------------------
# Here Lies Dead Code:
#
#   Prior to using the HashableModel, used this pydantic dataclass approach.
#   while this approach allows for hashing, it does not allow for the easy use
#   of serializing/deseralizing the data via the pydantic system.  Since we wnat
#   to use VlanProfile in test-cases, and store those test-cases as JSON files,
#   we neeed serialization functionality.

# @dataclass(frozen=True)
# class VlanProfile:
#     name: str
#     vlan_id: int = Field(..., ge=1, le=4094)
#     description: Optional[str] = Field(None)
#
#     def dict(self):
#         return asdict(self)
