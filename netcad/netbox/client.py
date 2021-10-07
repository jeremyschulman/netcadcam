# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Dict, List, Callable
import asyncio
from os import environ
from operator import itemgetter
from itertools import chain, starmap

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from httpx import AsyncClient
from tenacity import retry, wait_exponential

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["NetboxClient"]


# -----------------------------------------------------------------------------
#
#                              CODE BEGINS
#
# -----------------------------------------------------------------------------


class NetboxClient(AsyncClient):
    ENV_VARS = ["NETBOX_ADDR", "NETBOX_TOKEN"]
    DEFAULT_TIMEOUT = 60
    DEFAULT_PAGE_SZ = 1000
    API_RATE_LIMIT = 100

    API_DEVICES = "/dcim/devices/"
    API_INTERFACES = "/dcim/interfaces/"
    API_MFCS = "/dcim/manufacturers/"
    API_SITES = "/dcim/sites/"
    API_DEVICE_TYPES = "/dcim/device-types/"
    API_DEVICE_ROLES = "/dcim/device-roles/"
    API_LOCATIONS = "/dcim/locations/"
    API_CABLES = "/dcim/cables/"
    API_IP_ADDRESSES = "/ipam/ip-addresses/"
    API_TAGS = "/extras/tags/"

    def __init__(self, base_url=None, token=None, **kwargs):
        try:
            url = base_url or environ["NETBOX_ADDR"]
            token = token or environ["NETBOX_TOKEN"]
        except KeyError as exc:
            raise RuntimeError(f"Missing environment variable: {exc.args[0]}")

        kwargs.setdefault("verify", False)
        kwargs.setdefault("timeout", self.DEFAULT_TIMEOUT)

        super().__init__(
            base_url=f"{url}/api",
            **kwargs,
        )
        self.headers["Authorization"] = f"Token {token}"
        self._api_s4 = asyncio.Semaphore(self.API_RATE_LIMIT)

    async def request(self, *vargs, **kwargs):
        @retry(wait=wait_exponential(multiplier=1, min=4, max=10))
        async def _do_rqst():
            res = await super(NetboxClient, self).request(*vargs, **kwargs)

            if res.status_code in [500]:
                print(f"Netbox API error: {res.text}, retrying")
                res.raise_for_status()

            return res

        async with self._api_s4:
            return await _do_rqst()

    async def paginate_tasks(
        self, url: str, page_sz: Optional[int] = None, params: Optional[Dict] = None
    ):
        params = params or {}
        params["limit"] = 1

        res = await self.get(url, params=params)
        res.raise_for_status()
        body = res.json()
        count = body["count"]

        # create a list of tasks to run concurrently to fetch the data in pages.
        # NOTE: that we _MUST_ do a params.copy() to ensure that each task has a
        # unique offset count.  Observed that if copy not used then all tasks have
        # the same (last) value.

        params["limit"] = page_sz or self.DEFAULT_PAGE_SZ
        tasks = list()

        for offset in range(0, count, params["limit"]):
            params["offset"] = offset
            tasks.append(self.get(url, params=params.copy()))

        return tasks

    @staticmethod
    async def paginate_gather(tasks):
        task_results = await asyncio.gather(*tasks)

        # return the flattened list of results

        return list(
            chain.from_iterable(task_r.json()["results"] for task_r in task_results)
        )

    async def paginate(
        self, url: str, page_sz: Optional[int] = None, params: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Concurrently paginate GET on url for the given page_sz and optional
        Caller filters (Netbox API specific).  Return the list of all page
        results.

        Parameters
        ----------
        url:
            The Netbox API URL endpoint

        page_sz:
            Max number of result items

        params:
            Pass through of Netbox API parmaeters, specific to the API
            being paginated.

        Returns
        -------
        List of all Netbox API results from all pages
        """

        # GET the url for limit = 1 record just to determin the total number of
        # items.

        tasks = await self.paginate_tasks(url=url, page_sz=page_sz, params=params)
        return await self.paginate_gather(tasks)

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

    # -------------------------------------------------------------------------
    #
    #                        Device Interface Cabling Helper Methods
    #
    # -------------------------------------------------------------------------

    async def cable_interfaces(self, if_id_a: int, if_id_b: int) -> dict:
        res = await self.post(
            self.API_CABLES,
            json={
                "status": "connected",
                "termination_a_type": "dcim.interface",
                "termination_a_id": if_id_a,
                "termination_b_type": "dcim.interface",
                "termination_b_id": if_id_b,
            },
        )
        if res.is_error:
            raise RuntimeError(
                f"cable failured between {if_id_a}:{if_id_b} - {res.text}"
            )

        return res.json()

    # -------------------------------------------------------------------------
    #
    #                        Device Interface Helper Methods
    #
    # -------------------------------------------------------------------------

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
