from typing import Optional, AnyStr
from copy import deepcopy

import httpx


class ArangoClientBase(httpx.AsyncClient):
    DEFAULT_USERNAME = "root"
    DEFAULT_PASSWORD = ""
    DEFAULT_PORT = 8529
    DEFAULT_URL = f"http://127.0.0.1:{DEFAULT_PORT}"
    DEFAULT_AUTH = httpx.BasicAuth(username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD)

    def __init__(
        self,
        username: Optional[AnyStr] = None,
        password: Optional[AnyStr] = None,
        **kwargs,
    ):
        kwargs.setdefault("base_url", self.DEFAULT_URL)

        kwargs.setdefault("verify", False)
        self.auth = kwargs.pop("auth", self.DEFAULT_AUTH)

        if username or password:
            self.auth = httpx.BasicAuth(
                username or self.DEFAULT_USERNAME, password or self.DEFAULT_PASSWORD
            )

        kwargs["auth"] = self.auth
        self.__initkwargs = deepcopy(kwargs)
        super(ArangoClientBase, self).__init__(**kwargs)

    async def version(self, details=False):
        res = await self.get("/_api/version", params=dict(details=details))
        res.raise_for_status()
        return res.json()
