from typing import Dict

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
    interfaces: Dict[str, DeviceInterfaceType]
    consoles: Dict[str, DeviceConsoleType]

    def get_interface(self, if_name: str) -> DeviceInterfaceType:
        return self.interfaces.get(if_name)


class DeviceTypeRegistry(Registry, registry_name="device-type"):
    pass
