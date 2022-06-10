from enum import IntEnum


class BgpNeighborState(IntEnum):
    IDLE = 1
    CONNECT = 2
    ACTIVE = 3
    OPEN_SEND = 4
    OPEN_CONFIRM = 5
    ESTABLISHED = 6
