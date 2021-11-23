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
    # control-settings
    # -------------------------------------------------------------------------

    NETCAD_NOVALIDATE = auto()
