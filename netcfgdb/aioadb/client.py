from .base import ArangoClientBase
from .db import ArangoDatabase


class Aranago(ArangoClientBase):
    def db(self, name: str):
        return ArangoDatabase(name=name, parent=self)
