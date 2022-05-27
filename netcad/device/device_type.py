from typing import List

from pydantic import BaseModel

from netcad.registry import Registry
from netcad.phy_port import PhyPortSpeeds, PhyPortFormFactorType


class DeviceInterfaceType(BaseModel):
    name: str
    speed: PhyPortSpeeds
    formfactor: PhyPortFormFactorType


class DeviceConsoleType(BaseModel):
    name: str


class DeviceType(BaseModel):
    model: str
    product_model: str
    interfaces: List[DeviceInterfaceType]
    consoles: List[DeviceConsoleType]


class DeviceTypeRegistry(Registry, registry_name="device-type"):
    pass
