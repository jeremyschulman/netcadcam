# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Dict, Callable, Optional
import asyncio
from operator import itemgetter
from itertools import chain, starmap

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from .client import NetboxClient

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["NetboxDevices"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class NetboxDevices(NetboxClient):
    API_DEVICES = "/dcim/devices/"
    API_MFCS = "/dcim/manufacturers/"
    API_DEVICE_TYPES = "/dcim/device-types/"
    API_DEVICE_ROLES = "/dcim/device-roles/"

    API_INTERFACE_TEMPLATES = "/dcim/interface-templates/"

    # -------------------------------------------------------------------------
    #
    #                        Device Helper Methods
    #
    # -------------------------------------------------------------------------

    async def fetch_device(self, hostname):
        res = await self.get("/dcim/devices/", params=dict(name=hostname))
        res.raise_for_status()
        body = res.json()
        return [] if not body["count"] else body["results"]

    async def fetch_devices(self, hostname_list, key=None):
        res = await asyncio.gather(*(map(self.fetch_device, hostname_list)))
        flat = chain.from_iterable(res)
        if not key:
            return list(flat)

        key_fn = key if isinstance(key, Callable) else itemgetter(key)
        return {key_fn(rec): rec for rec in flat}

    async def fetch_device_type(self, slug: str) -> Dict:
        res = await self.get(self.API_DEVICE_TYPES, params=dict(slug=slug))
        res.raise_for_status()
        return res.json()

    async def fetch_device_template(self, **params) -> Optional[Dict]:

        res = await self.get(self.API_DEVICE_TYPES, params=params)
        res.raise_for_status()
        if not (payload := res.json()["results"]):
            return None

        device_type = payload[0]

        res = await self.get(
            self.API_INTERFACE_TEMPLATES,
            params=dict(devicetype_id=device_type["id"], limit=0),
        )
        res.raise_for_status()
        interfaces = list()
        res_if_list = res.json()["results"]

        for if_rec in res_if_list:
            del if_rec["display"]
            del if_rec["device_type"]
            del if_rec["url"]
            del if_rec["id"]
            del if_rec["last_updated"]
            del if_rec["created"]

            interfaces.append(if_rec)

        return {"device_type": device_type, "interfaces": interfaces}

    async def fetch_device_interface(self, hostname, if_name):
        res = await self.get(
            "/dcim/interfaces/", params=dict(device=hostname, name=if_name)
        )
        res.raise_for_status()
        body = res.json()
        return [] if not body["count"] else body["results"]

    async def fetch_devices_interfaces(self, items, key=None):
        res = await asyncio.gather(*(starmap(self.fetch_device_interface, items)))
        flat = chain.from_iterable(res)
        if not key:
            return list(flat)

        key_fn = key if isinstance(key, Callable) else itemgetter(key)  # noqa
        return {key_fn(rec): rec for rec in flat}
