#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ..devices import NetboxDevices
from ..cabling import NetboxCabling


class NetboxClient(NetboxDevices, NetboxCabling):
    ...


class NetboxTopologyOrigin:
    def __init__(self):
        self.api = NetboxClient()
