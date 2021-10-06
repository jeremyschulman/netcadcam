from http import HTTPStatus

from .base import ArangoClientBase


class ArangoDatabase(object):
    def __init__(self, name: str, parent: ArangoClientBase):
        self.name = name
        self.api = parent
        self.uri = f'_db/{self.name}'

    async def ensure(self, **options):
        db_list = await self.api.databases()
        if self.name in db_list:
            return self

        res = await self.api.post('/_api/database', json=dict(name=self.name, **options))
        res.raise_for_status()
        return self

    async def drop(self):
        res = await self.api.delete(f'/_api/database/{self.name}')

        # if the database is not found, then it does not exist, so AOK.
        if res.status_code == HTTPStatus.NOT_FOUND:
            return True

        # otherwise there was an error when attempting to delete the database.
        res.raise_for_status()

        # otherwise AOK.
        return True

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"


class ArangoCollection(object):
    def __init__(self, name: str, db: ArangoDatabase):
        self.name = name
        self.db = db
        self.uri = f'{self.db.uri}/_api/collection/{self.name}'

    async def ensure(self, **options):
        res = await self.db.api.post(f'{self.db.uri}/_api/collection', json=dict(name=self.name, **options))
        res.raise_for_status()
        return self

    async def drop(self):
        pass

    async def truncast(self):
        pass


class Aranago(ArangoClientBase):
    def db(self, name: str):
        return ArangoDatabase(name=name, parent=self)
