#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import PositiveInt, BaseModel, Field

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .phy_port_typedefs import (
    CableMediaType,
    CableTerminationType,
    PhyPortReachType,
    PhyPortFormFactorType,
)

from .phy_port_speeds import PhyPortSpeeds

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class PortCable(BaseModel):
    media: CableMediaType
    termination: CableTerminationType

    # `length` - when used, denotes the length of the cable in meters

    length: Optional[PositiveInt] = None


class PortTransceiver(BaseModel):
    # `form_factor` denotes the physical format of the transciver

    form_factor: PhyPortFormFactorType

    # `reach` denotes short or long range (or other tbd)

    reach: PhyPortReachType

    # 'type' - standard transceiver port-type, to match during validation
    #          see PhyPortTypes for standard values.

    type: str = None

    # `length` - when used, denotes the length of the cable in meters

    length: Optional[int] = None

    # `model` - when used, specific vendor model, to match during validation

    model: Optional[str] = None


class PhyPortProfile(BaseModel):
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

    # all that do not have a transceiver  need a form-factor defined.
    form_factor: Optional[PhyPortFormFactorType] = Field(default=None)

    # `poe` - when used, denotes if POE is enabled/disabled
    poe: Optional[bool] = Field(default=None)

    # `speed` - when used, changes the port default speed (megabits/sec)
    # 1_000 == 1Gbps, for example

    speed: Optional[PhyPortSpeeds] = Field(default=None)

    # `autoneg` - when used, enabled/disables auto-negotiation

    autoneg: Optional[bool] = Field(default=None)

    # `breakout` - when used, indicates the break port number [1-4]

    breakout: Optional[int] = Field(
        default=None,
        ge=1,
        le=4,
        description="",
    )
