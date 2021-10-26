# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Iterable, AnyStr

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic.dataclasses import dataclass

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .origin import Origin

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["OriginDeviceType", "OriginDeviceTypeInterfaceSpec"]


@dataclass()
class OriginDeviceTypeInterfaceSpec:
    if_name: str
    if_type: str
    if_type_label: str


class OriginDeviceType(Origin):
    def __init__(self, origin_spec):
        self.origin_spec = origin_spec

    @property
    def product_model(self) -> str:
        raise NotImplementedError()

    @property
    def interface_names(self) -> Iterable[AnyStr]:
        raise NotImplementedError()

    def get_interface(self, if_name: str) -> OriginDeviceTypeInterfaceSpec:
        raise NotImplementedError()

    @classmethod
    def load(cls, product_model: str) -> "OriginDeviceType":
        return cls.cache_load(
            cache_subdir="device-types", cache_item_name=product_model
        )

    async def save(self):
        await self.cache_save(
            cache_subdir="device-types",
            cache_item_name=self.product_model,
            payload=self.origin_spec,
        )

    @classmethod
    async def get(cls, product_models: Iterable[AnyStr]):
        """
        Gets the collection of product models from the origin and saves them to
        the cache filesystem.

        Parameters
        ----------
        product_models:
            List of product-model string values.
        """
        raise NotImplementedError()
