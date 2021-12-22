# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Dict, Optional
from copy import deepcopy
from types import ModuleType

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.registry import Registry
from netcad.device import Device
from netcad.notes import DesignNotes

# -----------------------------------------------------------------------------
# Private Module Imports
# -----------------------------------------------------------------------------

from .design_service import DesignService


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["Design", "DesignConfig", "DesignService"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


# TODO: for now the design configuration that comes from the "netcad.toml" file
#       is repreesnted into a dictionary object.  Future it will be a pydantic
#       modelled instance. this would be a code-breaking change.

DesignConfig = Dict


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
        # Register this design by designer designated name.  The name generally
        # comes from the name as defined in the netcad configuration file.

        self.registry_add(name=name, obj=self)
        self.name = name
        self.module: Optional[ModuleType] = None

        # collection of notes defined by the Designer
        self.notes = DesignNotes()
        self.notes.design = self

        # The config that originated from the netcad configuration file for this
        # specific design.

        self.config = deepcopy(config or {})

        # Caller designated named design services.  For example a designer could
        # call the VlanDesignService "vlans" or "my_vlans". The netcad system
        # does not hardcode any  speific names and leaves those decisions to the
        # designer.

        self.services: Dict[str, DesignService] = dict()

        self.devices: Dict[str, Device] = dict()

        self.ipams = dict()

    def add_devices(self, *devices: Device) -> "Design":
        """
        This method adds device(s) to the design instance.  The Designer MUST
        call this method for any device used in the design so that the device is
        accounted for, and the device.design backreference is established.

        Parameters
        ----------
        devices:
            Either a single Device instance or a list (or other iterable) of
            Device instances to add to the design.
        """

        for dev in devices:
            self.devices[dev.name] = dev
            dev.design = self

        # for method chaining
        return self

    def add_services(self, *design_services: DesignService) -> "Design":
        for svc in design_services:
            self.services[svc.name] = svc

        # for method chaining
        return self

    def build(self) -> "Design":
        """
        Execute the `build` methods for all services in the design.
        """
        for svc in self.services.values():
            svc.build()

        # for method chaining
        return self

    def validate(self):
        """
        Execute the `validate` methods for all services in the design.
        """
        for svc in self.services.values():
            svc.validate()

    def update(self):
        """
        This "helper" method is used to rebuild all services and then
        re-validate all services.  The expected use-case is when a Designer
        needs to update an existing design instance after it has already been
        gone through an original build+validate cycle.
        """
        self.build()
        self.validate()
