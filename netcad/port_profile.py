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


class PortCableMediaType(Enum):
    """Denotes the physical cable type"""

    SMF = enum.auto()
    MMF = enum.auto()
    CAT5 = enum.auto()
    CAT6 = enum.auto()
    CAT7 = enum.auto()


class PortCableTerminationType(Enum):
    """denotes the physical connector termitnating the cable"""

    LC = enum.auto()
    SC = enum.auto()
    ST = enum.auto()
    RJ45 = enum.auto()


class PortTranscieverFormFactorType(Enum):
    """denotes the transciever form-factor type"""

    AOC = enum.auto()
    SFP = enum.auto()
    SFPp = enum.auto()  # SFP+
    SFP28 = enum.auto()
    QSFP = enum.auto()
    QSFPp = enum.auto()  # QSFP+
    QSFP28 = enum.auto()
    RJ45 = enum.auto()


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


class PortCable(BaseModel):
    media: PortCableMediaType
    termination: PortCableTerminationType
    length: Optional[PositiveInt] = Field(
        default=None, description="when used, denotes the length of the cable in meters"
    )


class PortTransceiver(BaseModel):
    form_factor: PortTranscieverFormFactorType
    reach: PortTransceiverReachType
    length: Optional[int] = Field(
        default=None, description="when used, denotes the length of the cable in meters"
    )
    model: Optional[str] = Field(
        default=None,
        description="specific vendor model, when used, to match during validation",
    )


class PortProfile(BaseModel):
    """
    A PortProfile is used to identify the physical port criterial if-and-only-if
    a change from the default port is required.  Common usages of a PortProfile:

        - denote the use of a transceiver
        - denote the use of specific fiber cabling
        - denote the use of a breakout cable
        - denote specific speed setting

    A PortProfile would _not_ be used, for exaple if a switch port was 1G copper
    (RJ-45) and it is used "as-is".
    """

    speed: Optional[PositiveInt] = Field(
        description="When used, changes the port default speed (megabits/sec)"  # 1_000 == 1Gbps, for example
    )

    autoneg: Optional[bool] = Field(
        default=None, description="When used, enabled/disables auto-negotiation"
    )

    cabling: Optional[PortCable]

    transceiver: Optional[PortTransceiver]

    poe: Optional[bool] = Field(
        default=None, description="When used, denotes if POE is enabled/disabled"
    )

    breakout: Optional[int] = Field(
        default=None,
        ge=1,
        le=4,
        description="When used, indicates the break port number [1-4]",
    )
