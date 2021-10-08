from typing import Optional
from pydantic import BaseModel, PositiveInt, Field


class VlanProfile(BaseModel):
    name: str = Field(description="VLAN name")
    vlan_id: PositiveInt = Field(ge=1, le=4094, description="access VLAN ID")
    description: Optional[str]
