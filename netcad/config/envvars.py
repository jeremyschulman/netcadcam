from netcad.helpers import StrEnum
from enum import auto


class Environment(StrEnum):
    NETCAD_CONFIGFILE = auto()
    NETCAD_CACHEDIR = auto()
    NETCAD_PROJECTDIR = auto()
    NETCAD_TESTCASESDIR = auto()
    NETCAD_NOVALIDATE = auto()
