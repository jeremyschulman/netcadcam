#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from netcad.logger import get_logger

from ..netbox_cache import NetboxCache
from ..devices import NetboxDevices
from ..cabling import NetboxCabling
from .plugin_config import g_netbox_topology_config


class NetboxClient(NetboxDevices, NetboxCabling):
    ...


class NetboxTopologyOrigin:
    def __init__(self):
        self.config = g_netbox_topology_config
        self.name = self.config["service"]
        self.api = NetboxClient()
        self.cache = NetboxCache()
        self.log = get_logger()
        self.log_origin = "origin/Netbox:Topology"
        self.devices = dict()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.api.aclose()
