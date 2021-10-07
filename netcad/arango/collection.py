from http import HTTPStatus

from .db import ArangoDatabase


class ArangoCollection(object):
    API_COLLECTION = "/_api/collection"

    def __init__(self, name: str, db: "ArangoDatabase", **options):
        self.name = name
        self.db = db
        self.options = options
        self.uri = f"{self.db.uri}{self.API_COLLECTION}/{self.name}"

    async def ensure(self, **options):
        self.options.update(**options)

        res = await self.db.api.post(
            f"{self.db.uri}{self.API_COLLECTION}",
            json=dict(name=self.name, **self.options),
        )

        # 409 means the collection already exists, so AOK.
        if res.status_code == HTTPStatus.CONFLICT:
            return self

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
