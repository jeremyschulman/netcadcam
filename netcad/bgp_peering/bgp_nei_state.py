from enum import auto
from netcad.helpers import StrEnum


# due to bug in PyCharm, ...
# noinspection PyArgumentList
class BgpNeighborState(StrEnum):
    IDLE = auto()
    CONNECT = auto()
    ACTIVE = auto()
    OPEN_SENT = auto()
    OPEN_CONFIRM = auto()
    ESTABLISHED = auto()
