from typing import Optional
from collections import defaultdict

from bracket_expansion import expand
from .device_type import DeviceType, DeviceTypeRegistry


__all__ = ["DeviceTypeFactory"]


class DeviceTypeFactory:
    def __init__(self, model: str, suffix: Optional[str] = None):
        self.model = model
        self.product_model = model if not suffix else model + suffix
        self._items = defaultdict(list)
        ...

    def interfaces(self, namespec: str, **kwargs):
        for if_name in expand(namespec):
            self._items["interfaces"].append(dict(name=if_name, **kwargs))

        return self

    def console(self, namespec: str, **kwargs):
        for name in expand(namespec):
            self._items["consoles"].append(dict(name=name, **kwargs))
        return self

    def build(self) -> DeviceType:
        dt = DeviceType(
            model=self.model, product_model=self.product_model, **self._items
        )
        DeviceTypeRegistry.registry_add(self.product_model, dt)
        return dt
