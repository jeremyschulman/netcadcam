from typing import Dict, Optional
from copy import deepcopy

from netcad.registry import Registry
from netcad.device import Device

from .design_service import DesignService


class Design(Registry, registry_name="designs"):
    """
    A `Design` instance is used to contain all conceptual elements related to a
    given design.  When a User invoke the netcad/netcam tools and refernces a
    design by name, it is a Design instance that is used to contain all aspects
    of that design.

    Attributes
    ----------
    services: dict
    devices: dict
    ipams: dict
    """

    def __init__(self, name: str, config: Optional[Dict] = None):

        self.registry_add(name=name, obj=self)
        self.services: Dict[str, DesignService] = dict()
        self.devices: Dict[str, Device] = dict()
        self.ipams = dict()
        self.config = deepcopy(config or {})
