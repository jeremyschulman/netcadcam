# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Dict, List
import asyncio
from os import environ
from itertools import chain

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
