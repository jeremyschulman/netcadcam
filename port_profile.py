# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional
from enum import Enum
import enum

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, Field, PositiveInt

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["PortProfile", "PortMediumType", "PortConnectorType"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class PortMediumType(Enum):
    SMF = enum.auto()
    MMF = enum.auto()
    CAT6 = enum.auto()


class PortConnectorType(Enum):
    LC = enum.auto()
    SC = enum.auto()
    ST = enum.auto()
    RJ45 = enum.auto()


class PortProfile(BaseModel):
    speed: PositiveInt = Field(
        description="port speed in megabits/sec"  # 1_000 == 1Gbps, for example
    )
    medium: PortMediumType
    connector: PortConnectorType
    poe: Optional[bool] = Field(default=False)
    breakout: Optional[int] = Field(
        default=0, le=4, description="indicates the break port number when used"
    )
