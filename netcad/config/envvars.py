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
    NETCAD_TESTCASESDIR = auto()
    NETCAD_TEMPLATESDIR = auto()

    # -------------------------------------------------------------------------
    # Controls
    # -------------------------------------------------------------------------

    NETCAD_NOVALIDATE = auto()

    # When defined instructs the netcad system to use this design name, or
    # collection of design naames when using colon-separated values, so that the
    # User does not need to provide the --design flag option to CLI commands.

    NETCAD_DESIGNS = auto()
