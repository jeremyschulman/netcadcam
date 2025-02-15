#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Dict, Optional, List, Any, Type
from copy import deepcopy
from types import ModuleType

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.registry import Registry
from netcad.device import Device
from netcad.notepad import Notepad
from netcad.ipam import IPAM

# -----------------------------------------------------------------------------
# Private Module Imports
# -----------------------------------------------------------------------------

from netcad.services.design_service import DesignService
from .design_feature import DesignFeature

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["Design", "DesignConfig", "DesignFeature"]

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
    features: dict
    devices: dict
    ipams: dict
    """

    def __init__(self, name: str, config: Optional[Dict] = None):
        # Register this design by designer designated name.  The name generally
        # comes from the name as defined in the netcad configuration file.

        self.registry_add(name=name, obj=self)
        self.name = name
        self.module: Optional[ModuleType] = None

        # if the design groups other designs, then the `group` attribute holds
        # that list of design-names.

        self.group: Optional[List[str]] = None

        # collection of notepad defined by the Designer
        self.notes: Notepad["Design"] = Notepad(self)
        self.notes.design = self

        # The config that originated from the netcad configuration file for this
        # specific design.

        self.config = deepcopy(config or {})

        # Caller designated named design features.  For example a designer could
        # call the VlanDesignService "vlans" or "my_vlans". The netcad system
        # does not hardcode any  speific names and leaves those decisions to the
        # designer.

        self.features: Dict[str, DesignFeature] = dict()

        # Design services, key=name, value=service instance.  These are the services that the
        # designer has defined to be used in the design.  The netcad system does
        # not hardcode any specific names and leaves those decisions to the designer.

        self.services: Dict[str, DesignService] = dict()

        # key=device.alias, value=Device instance
        self.devices: Dict[str, Device] = dict()

        self.ipams: Dict[Any, IPAM] = dict()

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
            self.devices[dev.alias] = dev
            dev.design = self

        # for method chaining
        return self

    def add_feature(self, *design_services: DesignFeature) -> "Design":
        for svc in design_services:
            self.features[svc.name] = svc

        # for method chaining
        return self

    def build(self) -> "Design":
        """
        Execute the `build` methods for all features in the design.
        """
        for svc in self.features.values():
            svc.build()

        # for method chaining
        return self

    def validate(self):
        """
        Execute the `validate` methods for all features in the design.
        """
        for svc in self.features.values():
            svc.validate()

    def update(self):
        """
        This "helper" method is used to rebuild all features and then
        re-validate all features.  The expected use-case is when a Designer
        needs to update an existing design instance after it has already been
        gone through an original build+validate cycle.
        """
        self.build()
        self.validate()

    def feature_of(self, svc_cls: Type[DesignFeature]) -> List[DesignFeature]:
        """Return the features that are of the given service type"""
        return [svc for svc in self.features.values() if isinstance(svc, svc_cls)]
