from typing import Optional
from pydantic.dataclasses import dataclass, Field


@dataclass
class VlanProfile:
    name: str
    vlan_id: int = Field(..., ge=1, le=4094)
    description: Optional[str] = Field(None)
