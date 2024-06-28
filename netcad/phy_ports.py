"""
This file contains the physicl port profile definitions used by the MLB network
infrastructure as code design files.

References
----------
Transceivers:
    https://www.arista.com/assets/data/pdf/Arista100G_TC_QA.pdf

"""

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from netcad.phy_port import (
    PhyPortProfile,
    PortTransceiver,
    PhyPortReachType,
    PhyPortFormFactorType,
    PortCable,
    CableMediaType,
    CableTerminationType,
    PhyPortSpeeds,
    PhyPortTypes,
)

# -----------------------------------------------------------------------------
#
#                           100 Gigabit Ethernet
#
# -----------------------------------------------------------------------------

QSFP_100G_AOC = PhyPortProfile(
    name="QSFP-100G-AOC",
    speed=PhyPortSpeeds.speed_100G,
    cabling=PortCable(media=CableMediaType.AOC, termination=CableTerminationType.AOC),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.QSFP,
        type=PhyPortTypes.type_100GBASE_AOC,
        reach=PhyPortReachType.short,
    ),
)

QSFP_100G_LR4 = PhyPortProfile(
    name="QSFP-100G-LR4",
    speed=PhyPortSpeeds.speed_100G,
    cabling=PortCable(media=CableMediaType.SMF, termination=CableTerminationType.LC),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.QSFP,
        type=PhyPortTypes.type_100GBASE_LR4,
        reach=PhyPortReachType.long,
    ),
)

QSFP_100G_SR4 = PhyPortProfile(
    name="QSFP-100G-SR4",
    speed=PhyPortSpeeds.speed_100G,
    cabling=PortCable(media=CableMediaType.MMF, termination=CableTerminationType.LC),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.QSFP,
        type=PhyPortTypes.type_100GBASE_SR4,
        reach=PhyPortReachType.long,
    ),
)

QSFP_100G_CWDM4 = PhyPortProfile(
    name="QSFP-100G-CWDM4",
    speed=PhyPortSpeeds.speed_100G,
    cabling=PortCable(media=CableMediaType.MMF, termination=CableTerminationType.MPO),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.QSFP28,
        type=PhyPortTypes.type_100GBASE_CWDM4,
        reach=PhyPortReachType.short,
    ),
)

QSFP_100G_SWDM4 = PhyPortProfile(
    name="QSFP-100G-SWDM4",
    speed=PhyPortSpeeds.speed_100G,
    cabling=PortCable(media=CableMediaType.MMF, termination=CableTerminationType.MPO),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.QSFP28,
        type=PhyPortTypes.type_100GBASE_SWDM4,
        reach=PhyPortReachType.short,
    ),
)

QSFP_100G_SRBD = PhyPortProfile(
    name="QSFP-100G-SRBD",
    speed=PhyPortSpeeds.speed_100G,
    cabling=PortCable(media=CableMediaType.MMF, termination=CableTerminationType.LC),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.QSFP28,
        type=PhyPortTypes.type_100GBASE_SRBD,
        reach=PhyPortReachType.short,
    ),
)

# -----------------------------------------------------------------------------
#
#                           40 Gigabit Ethernet
#
# -----------------------------------------------------------------------------

QSFP_40G = PhyPortProfile(
    name="QSFP-40G",
    speed=PhyPortSpeeds.speed_40G,
)

QSFP_40G_LR4 = PhyPortProfile(
    name="QSFP-40G-LR4",
    speed=PhyPortSpeeds.speed_40G,
    cabling=PortCable(media=CableMediaType.SMF, termination=CableTerminationType.LC),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.QSFP,
        type=PhyPortTypes.type_40GBASE_LR4,
        reach=PhyPortReachType.long,
    ),
)

QSFP_40G_SR4 = PhyPortProfile(
    name="QSFP-40G-SR4",
    speed=PhyPortSpeeds.speed_40G,
    cabling=PortCable(media=CableMediaType.MMF, termination=CableTerminationType.LC),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.QSFP,
        type=PhyPortTypes.type_40GBASE_SR4,
        reach=PhyPortReachType.short,
    ),
)

QSFP_40G_AOC = PhyPortProfile(
    name="QSFP-40G-AOC",
    speed=PhyPortSpeeds.speed_40G,
    cabling=PortCable(media=CableMediaType.MMF, termination=CableTerminationType.AOC),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.QSFP28,
        type=PhyPortTypes.type_40GBASE_AOC,
        reach=PhyPortReachType.short,
    ),
)

QSFP_40G_SRBD = PhyPortProfile(
    name="QSFP-40G-SRBD",
    speed=PhyPortSpeeds.speed_40G,
    cabling=PortCable(media=CableMediaType.MMF, termination=CableTerminationType.LC),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.QSFP28,
        type=PhyPortTypes.type_40GBASE_SRBD,
        reach=PhyPortReachType.short,
    ),
)

# -----------------------------------------------------------------------------
#
#                           25 Gigabit Ethernet
#
# -----------------------------------------------------------------------------

SFP28_25G_CR = PhyPortProfile(
    name="SFP28-25GBASE-CR",
    speed=PhyPortSpeeds.speed_25G,
    cabling=PortCable(media=CableMediaType.DAC, termination=CableTerminationType.DAC),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.SFP28,
        type=PhyPortTypes.type_25GBASE_CR,
        reach=PhyPortReachType.short,
    ),
)

SFP28_25CR_10G = PhyPortProfile(
    name="SFP28-25GBASE-CR",
    speed=PhyPortSpeeds.speed_10G,
    cabling=PortCable(media=CableMediaType.DAC, termination=CableTerminationType.DAC),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.SFP28,
        type=PhyPortTypes.type_25GBASE_CR,
        reach=PhyPortReachType.short,
    ),
)

# SFPP_25G_DAC = PhyPortProfile(
#     name="SFP28-25G-DAC",
#     speed=PhyPortSpeeds.speed_25G,
#     cabling=PortCable(media=CableMediaType.DAC, termination=CableTerminationType.DAC),
#     transceiver=PortTransceiver(
#         form_factor=PhyPortFormFactorType.SFP28,
#         type=PhyPortTypes.type_25GBASE_CR,
#         reach=PhyPortReachType.short,
#     ),
# )

SFPP_25G_SR = PhyPortProfile(
    name="SFPP-25G-SR",
    speed=PhyPortSpeeds.speed_25G,
    cabling=PortCable(media=CableMediaType.SMF, termination=CableTerminationType.LC),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.SFP28,
        type=PhyPortTypes.type_25GBASE_SR,
        reach=PhyPortReachType.short,
    ),
)

SFPP_25G_LR = PhyPortProfile(
    name="SFPP-25G-LR",
    speed=PhyPortSpeeds.speed_25G,
    cabling=PortCable(media=CableMediaType.SMF, termination=CableTerminationType.LC),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.SFP28,
        type=PhyPortTypes.type_25GBASE_LR,
        reach=PhyPortReachType.long,
    ),
)

# -----------------------------------------------------------------------------
#
#                           10 Gigabit Ethernet
#
# -----------------------------------------------------------------------------

SFPP_10G_CR = PhyPortProfile(
    name="SFPP-10G-CR",
    speed=PhyPortSpeeds.speed_10G,
    cabling=PortCable(media=CableMediaType.DAC, termination=CableTerminationType.DAC),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.SFPP,
        type=PhyPortTypes.type_10GBASE_CR,
        reach=PhyPortReachType.short,
    ),
)

# the DAC term is the same as CR
SFPP_10G_DAC = SFPP_10G_CR

SFPP_10G_AOC = PhyPortProfile(
    name="SFPP-10G-AOC",
    speed=PhyPortSpeeds.speed_10G,
    cabling=PortCable(media=CableMediaType.AOC, termination=CableTerminationType.AOC),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.SFPP,
        type=PhyPortTypes.type_10GBASE_AOC,
        reach=PhyPortReachType.short,
    ),
)


SFPP_10G_LR = PhyPortProfile(
    name="SFPP-10G-LR",
    speed=PhyPortSpeeds.speed_10G,
    cabling=PortCable(media=CableMediaType.SMF, termination=CableTerminationType.LC),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.SFPP,
        type=PhyPortTypes.type_10GBASE_LR,
        reach=PhyPortReachType.long,
    ),
)

SFPP_10G_SR = PhyPortProfile(
    name="SFPP-10G-SR",
    speed=PhyPortSpeeds.speed_10G,
    cabling=PortCable(media=CableMediaType.SMF, termination=CableTerminationType.LC),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.SFPP,
        type=PhyPortTypes.type_10GBASE_SR,
        reach=PhyPortReachType.short,
    ),
)

SFPP_10G_T = PhyPortProfile(
    name="SFPP-10G-T",
    speed=PhyPortSpeeds.speed_10G,
    cabling=PortCable(media=CableMediaType.CAT6, termination=CableTerminationType.RJ45),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.SFP,
        type=PhyPortTypes.type_10GBASE_T,
        reach=PhyPortReachType.short,
    ),
)

# -----------------------------------------------------------------------------
#
#                           multi Gigabit Ethernet
#
# -----------------------------------------------------------------------------

CAT6_2dot5_RJ45 = PhyPortProfile(
    name="CAT6-2.5G-RJ45",
    speed=PhyPortSpeeds.speed_2_5G,
    form_factor=PhyPortFormFactorType.RJ45,
    cabling=PortCable(media=CableMediaType.CAT6, termination=CableTerminationType.RJ45),
)

CAT6_5G_RJ45 = PhyPortProfile(
    name="CAT6-5G-RJ45",
    speed=PhyPortSpeeds.speed_5G,
    form_factor=PhyPortFormFactorType.RJ45,
    cabling=PortCable(media=CableMediaType.CAT6, termination=CableTerminationType.RJ45),
)

# -----------------------------------------------------------------------------
#
#                           1 Gigabit Ethernet
#
# -----------------------------------------------------------------------------

CAT6_1G_RJ45 = PhyPortProfile(
    name="CAT6-1G-RJ45",
    speed=PhyPortSpeeds.speed_1G,
    form_factor=PhyPortFormFactorType.RJ45,
    cabling=PortCable(media=CableMediaType.CAT6, termination=CableTerminationType.RJ45),
)

SFP_1G_T = PhyPortProfile(
    name="SFP-1G-T",
    speed=PhyPortSpeeds.speed_1G,
    cabling=PortCable(media=CableMediaType.CAT6, termination=CableTerminationType.RJ45),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.SFP,
        type=PhyPortTypes.type_1000BASE_T,
        reach=PhyPortReachType.short,
    ),
)

SFP_1G_LX = PhyPortProfile(
    name="SFP-1G-LX",
    speed=PhyPortSpeeds.speed_1G,
    cabling=PortCable(media=CableMediaType.SMF, termination=CableTerminationType.LC),
    transceiver=PortTransceiver(
        form_factor=PhyPortFormFactorType.SFP,
        type=PhyPortTypes.type_1000BASE_LX,
        reach=PhyPortReachType.long,
    ),
)

# -----------------------------------------------------------------------------
#
#                           100 Mbps Ethernet
#
# -----------------------------------------------------------------------------

CAT6_100M_RJ45 = PhyPortProfile(
    name="CAT6-100M-RJ45",
    speed=PhyPortSpeeds.speed_100M,
    form_factor=PhyPortFormFactorType.RJ45,
    cabling=PortCable(media=CableMediaType.CAT6, termination=CableTerminationType.RJ45),
)
