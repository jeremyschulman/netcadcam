# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional
import enum

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import PositiveInt
from pydantic.dataclasses import dataclass, Field

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.helpers import StrEnum

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class PortCableMediaType(StrEnum):
    """Denotes the physical cable type"""

    SMF = enum.auto()
    MMF = enum.auto()
    CAT5 = enum.auto()
    CAT6 = enum.auto()
    CAT7 = enum.auto()
    AOC = enum.auto()
    TWX = enum.auto()  # twinaxial


class PortCableTerminationType(StrEnum):
    """denotes the physical connector termitnating the cable"""

    LC = enum.auto()
    SC = enum.auto()
    ST = enum.auto()
    RJ45 = enum.auto()
    AOC = enum.auto()
    TWX = enum.auto()


class PortTranscieverFormFactorType(StrEnum):
    """denotes the transciever form-factor type"""

    AOC = enum.auto()
    SFP = enum.auto()
    SFPP = enum.auto()  # SFP+
    SFP28 = enum.auto()
    QSFP = enum.auto()
    QSFPP = enum.auto()  # QSFP+
    QSFP28 = enum.auto()
    RJ45 = enum.auto()


class PortTransceiverReachType(StrEnum):
    short = enum.auto()
    long = enum.auto()


# # common port speeds
#
# PORT_SPEED_1G = 1_000
# PORT_SPEED_2_5G = 2_500  # 2.5 Gbps
# PORT_SPEED_5G = 5_000
# PORT_SPEED_10G = 10_000
# PORT_SPEED_25G = 25_000
# PORT_SPEED_40G = 40_000
# PORT_SPEED_100G = 100_000


@dataclass
class PortCable:
    media: PortCableMediaType
    termination: PortCableTerminationType

    # `length` - when used, denotes the length of the cable in meters

    length: Optional[PositiveInt] = None


@dataclass
class PortTransceiver:

    # `form_factor` denotes the physical format of the transciver

    form_factor: PortTranscieverFormFactorType

    # `reach` denotes short or long range (or other tbd)

    reach: PortTransceiverReachType

    # 'type' - standard transceiver port-type, to match during validation
    #          see PhyPortTypes for standard values.

    type: str = None

    # `length` - when used, denotes the length of the cable in meters

    length: Optional[int] = None

    # `model` - when used, specific vendor model, to match during validation

    model: Optional[str] = None


@dataclass
class PortProfile:
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

    name: str

    # `cabling` - when used, identifies the type of cable expected to be used
    # with this port.  Includes for cable-planning design related tasks.

    cabling: Optional[PortCable]

    # `transceiver` - when used, identifies the transceiver expected to be
    # inserted into the physical port; or use of breakout.

    transceiver: Optional[PortTransceiver]

    # `poe` - when used, denotes if POE is enabled/disabled

    poe: Optional[bool] = Field(None)

    # `speed` - when used, changes the port default speed (megabits/sec)
    # 1_000 == 1Gbps, for example

    speed: Optional[PositiveInt] = Field(None)

    # `autoneg` - when used, enabled/disables auto-negotiation

    autoneg: Optional[bool] = Field(None)

    # `breakout` - when used, indicates the break port number [1-4]

    breakout: Optional[int] = Field(
        default=None,
        ge=1,
        le=4,
        description="",
    )
