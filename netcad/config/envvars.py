#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from netcad.helpers import StrEnum
from enum import auto


class Environment(StrEnum):
    # -------------------------------------------------------------------------
    # files
    # -------------------------------------------------------------------------

    NETCAD_CONFIGFILE = auto()

    # -------------------------------------------------------------------------
    # directories
    # -------------------------------------------------------------------------

    NETCAD_CACHEDIR = auto()
    NETCAD_PROJECTDIR = auto()
    NETCAD_CONFIGSDIR = auto()
    NETCAD_CHECKSDIR = auto()
    NETCAD_TEMPLATESDIR = auto()

    # -------------------------------------------------------------------------
    # Controls
    # -------------------------------------------------------------------------

    NETCAD_NOVALIDATE = auto()

    # When defined instructs the netcad system to use this design name, or
    # collection of design naames when using colon-separated values, so that the
    # User does not need to provide the --design flag option to CLI commands.

    NETCAD_DESIGN = auto()
