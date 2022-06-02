from typing import Optional
from collections import defaultdict

from bracket_expansion import expand
from .device_type import DeviceType, DeviceTypeRegistry


__all__ = ["DeviceTypeFactory"]


class DeviceTypeFactory:
    def __init__(self, model: str, suffix: Optional[str] = None):
        self.model = model
        self.product_model = model if not suffix else model + suffix

        # various device items, arranged by the type of item, such as
        # 'interfaces', each of which is a dict key=name and value=fields.

        self._items = defaultdict(dict)

    def interfaces(self, namespec: str, **kwargs):
        for if_name in expand(namespec):
            self._items["interfaces"][if_name] = dict(name=if_name, **kwargs)

        return self

    def console(self, namespec: Optional[str] = "console", **kwargs):
        for name in expand(namespec):
            self._items["consoles"][name] = dict(name=name, **kwargs)
        return self

    def build(self, name: str = None) -> DeviceType:
        """
        Create the DeviceType instance and register it into the
        DeviceTypeRegistry using either the give 'name' or the 'product_model'
        value as the name.

        Parameters
        ----------
        name: str, optional
            When given this name is ued to register this DeviceType into the
            registry.

        Returns
        -------
        DeviceType - the newly create DeviceType instance.
        """
        dt = DeviceType(
            model=self.model, product_model=self.product_model, **self._items
        )
        DeviceTypeRegistry.registry_add(name or self.product_model, dt)
        return dt
