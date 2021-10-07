from typing import List

from .base import ArangoClientBase
from .db import ArangoDatabase


class ArangoClient(ArangoClientBase):
    async def db_list(self) -> List[str]:
        res = await self.get("/_api/database")
        res.raise_for_status()
        return res.json()["result"]

    def db(self, name: str):
        return ArangoDatabase(name=name, parent=self)
