from http import HTTPStatus

from .base import ArangoClientBase


class ArangoCollection(object):
    API_COLLECTION = "/_api/collection"

    def __init__(self, name: str, db: "ArangoDatabase"):
        self.name = name
        self.db = db
        self.uri = f"{self.db.uri}{self.API_COLLECTION}/{self.name}"

    async def ensure(self, **options):
        res = await self.db.api.post(
            f"{self.db.uri}{self.API_COLLECTION}", json=dict(name=self.name, **options)
        )
        res.raise_for_status()
        return self

    async def drop(self):
        res = await self.db.api.delete(f"{self.db.uri}{self.API_COLLECTION}")
        if res.status_code == HTTPStatus.NOT_FOUND:
            return True

        res.raise_for_status()
        return True

    async def truncate(self):
        res = await self.db.api.put(f"{self.db.uri}{self.API_COLLECTION}/truncate")
        res.raise_for_status()
        return self

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"


class ArangoDatabase(object):
    API_DATABASE = "/_api/database"

    def __init__(self, name: str, parent: ArangoClientBase):
        self.name = name
        self.api = parent
        self.uri = f"_db/{self.name}"

    async def ensure(self, **options):
        db_list = await self.api.databases()
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

    def collection(self, name: str):
        return ArangoCollection(name=name, db=self)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"
