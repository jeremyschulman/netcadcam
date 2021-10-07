from http import HTTPStatus
from .db import ArangoDatabase


class ArangoGraph(object):
    API_GRAPH = "/_api/gharial"

    def __init__(self, name: str, db: ArangoDatabase, **options):
        self.options = options
        self.name = name
        self.api = db.api
        self.db = db
        self.uri = f"{self.db.uri}{self.API_GRAPH}/{self.name}"

    async def ensure(self, **options):
        self.options.update(options)

        res = await self.db.api.post(
            f"{self.db.uri}{self.API_GRAPH}",
            json=dict(name=self.name, **self.options),
        )

        # 409 means the collection already exists, so AOK.
        if res.status_code == HTTPStatus.CONFLICT:
            return self

        res.raise_for_status()
        return self
