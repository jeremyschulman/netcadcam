from typing import Optional, Dict
from collections import defaultdict

from .client import NetboxClient


class NetboxCache(defaultdict):
    def __init__(self):
        super(NetboxCache, self).__init__(dict)

    async def fetch(
        self,
        client: NetboxClient,
        url: str,
        key: Optional[str] = "name",
        value: Optional[str] = None,
        params: Optional[Dict] = None,
    ) -> Optional[dict]:
        if not (lkup := tuple(params.items()) if params else value):
            raise ValueError("missing params or value")

        if (obj := self[url].get(lkup)) is not None:
            return obj

        get_params = params if params else {key: value}

        res = await client.get(url, params=get_params)
        res.raise_for_status()
        body = res.json()
        if not (count := body["count"]):
            return None

        results = body["results"]
        obj = results if count > 1 else results[0]

        self[url][lkup] = obj
        return obj

    def cache_clear(
        self,
        url: str,
        value: Optional[str] = None,
        params: Optional[Dict] = None,
    ):
        if not (lkup := tuple(params.items()) if params else value):
            raise ValueError("Missing params or value")

        if lkup in self[url]:
            del self[url][lkup]
