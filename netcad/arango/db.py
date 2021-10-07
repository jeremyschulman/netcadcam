from typing import TYPE_CHECKING
from http import HTTPStatus


if TYPE_CHECKING:
    from .client import ArangoClient


class ArangoDatabase(object):
    API_DATABASE = "/_api/database"

    def __init__(self, name: str, parent: "ArangoClient"):
        self.name = name
        self.api = parent
        self.uri = f"_db/{self.name}"

    async def ensure(self, **options):
        db_list = await self.api.db_list()
        if self.name in db_list:
            return self

        res = await self.api.post(
            self.API_DATABASE, json=dict(name=self.name, **options)
        )

        res.raise_for_status()
        return self

    async def drop(self):
        res = await self.api.delete(f"{self.API_DATABASE}/{self.name}")

        # if the database is not found, then it does not exist, so AOK.
        if res.status_code == HTTPStatus.NOT_FOUND:
            return True

        # otherwise there was an error when attempting to delete the database.
        res.raise_for_status()

        # otherwise AOK.
        return True

    def collection(self, name: str, **options):
        from .collection import ArangoCollection

        return ArangoCollection(name=name, db=self, **options)

    def graph(self, name: str, **options):
        from .graph import ArangoGraph

        return ArangoGraph(name=name, db=self, **options)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"
