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


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class PortCableType(Enum):
    """Denotes the physical cable type"""

    SMF = enum.auto()
    MMF = enum.auto()
    CAT6 = enum.auto()


class PortCableTerminationType(Enum):
    """denotes the physical connector termitnating the cable"""

    LC = enum.auto()
    SC = enum.auto()
    ST = enum.auto()
    RJ45 = enum.auto()


class PortTranscieverType(Enum):
    AOC = enum.auto()
    SFP = enum.auto()
    SFP_p = enum.auto()  # SFP+
    SFP28 = enum.auto()
    QSFP = enum.auto()
    QSFP_p = enum.auto()  # QSFP+
    QSFP28 = enum.auto()
    RJ45 = enum.auto()


class PortPoeType(Enum):
    pass


class PortTransceiverReachType(Enum):
    short = enum.auto()
    long = enum.auto()


# common port speeds

PORT_SPEED_1G = 1_000
PORT_SPEED_2_5G = 2_500  # 2.5 Gbps
PORT_SPEED_5G = 5_000
PORT_SPEED_10G = 10_000
PORT_SPEED_25G = 25_000
PORT_SPEED_40G = 40_000
PORT_SPEED_100G = 100_000


class PortProfile(BaseModel):
    speed: PositiveInt = Field(
        description="port speed in megabits/sec"  # 1_000 == 1Gbps, for example
    )
    cable_type: PortCableType
    cable_termination: PortCableTerminationType
    poe: Optional[bool] = Field(
        default=False, description="denotes if POE is supported"
    )
    breakout: Optional[int] = Field(
        default=0, le=4, description="indicates the break port number when used"
    )
