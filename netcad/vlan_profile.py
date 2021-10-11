from typing import Optional
from pydantic.dataclasses import dataclass, Field


@dataclass(frozen=True)
class VlanProfile:
    name: str
    vlan_id: int = Field(..., ge=1, le=4094)
    description: Optional[str] = Field(None)


# declare a sentinal instance to indicate that all VLANs defined on a device
# should be used. this is a common use-case for uplink trunk ports.

VLANS_ALL = [VlanProfile(name="*", vlan_id=1)]
