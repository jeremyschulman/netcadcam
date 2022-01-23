#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from collections import defaultdict

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from httpx import Response

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.design import Design
from netcad.igather import as_completed

# -----------------------------------------------------------------------------
# Private Module Imports
# -----------------------------------------------------------------------------

from ..netbox_cache import NetboxCache
from ..devices import NetboxDevices
from ..cabling import NetboxCabling
from .plugin_config import g_netbox_topology_config

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["NetboxTopologyOrigin"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class NetboxClient(NetboxDevices, NetboxCabling):
    ...


class NetboxTopologyOrigin:
    """origin for netbox topology service plugin"""

    def __init__(self):
        """construct the origin instance for push to netbox topology service"""
        self.config = g_netbox_topology_config
        self.name = self.config["service"]
        self.api = NetboxClient()
        self.cache = NetboxCache()
        self.log = get_logger()
        self.log_origin = f"origin/netbox:{self.name}"

        # cached netbox device records, key=hostname, value=rec-dict

        self.devices = dict()

        # cached netbox device interfaces, key1=hostname, key2=interface-name
        # value=netbox-interface-rec-dict

        self.interfaces = defaultdict(dict)

    async def fetch_devices(self, design: Design):
        tasks = {self.api.fetch_device(hostname=name): name for name in design.devices}
        async for coro, devrecs in as_completed(tasks):
            hostname = tasks[coro]
            self.devices[hostname] = next(iter(devrecs), None)

    async def fetch_interfaces(self):
        tasks = {
            self.api.paginate(
                "/dcim/interfaces/", params=dict(device_id=devrec["id"])
            ): devrec
            for devrec in self.devices.values()
        }

        res: Response
        async for coro, intf_recs in as_completed(tasks):
            devrec = tasks[coro]
            hostname = devrec["name"]
            for intf_rec in intf_recs:
                self.interfaces[hostname][intf_rec["name"]] = intf_rec

    # -------------------------------------------------------------------------
    # OVERLOADS: object
    # -------------------------------------------------------------------------

    async def __aenter__(self):
        """async context manager returns self"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """async context manager closes netbox client session"""
        await self.api.aclose()
