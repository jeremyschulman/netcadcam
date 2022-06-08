from typing import Optional, TypeVar
from enum import Enum

from pydantic import BaseModel


P = TypeVar("P")


class IpNetworkEnum(BaseModel):
    name: str
    address: str
    parent: Optional[P]


class IpNetworkEnumCatalog(Enum):
    @property
    def name(self):
        return self.value.name

    @property
    def address(self):
        return self.value.address

    @property
    def parent(self):
        return self.value.parent
