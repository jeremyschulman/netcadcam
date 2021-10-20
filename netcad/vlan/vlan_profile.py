from typing import Optional

from dataclasses import asdict
from pydantic.dataclasses import dataclass, Field


@dataclass(frozen=True)
class VlanProfile:
    name: str
    vlan_id: int = Field(..., ge=1, le=4094)
    description: Optional[str] = Field(None)

    def dict(self):
        return asdict(self)
