#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# Systeme Imports
# -----------------------------------------------------------------------------

from typing import Optional, TypeVar
from copy import copy

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.cabling import CableByCableId
from netcad.design.design_feature import DesignFeature


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["TopologyDesignFeature", "TopologyFeatureLike"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class TopologyDesignFeature(DesignFeature, registry_name="topology"):
    """
    The TopologyDesignFeature is required for every design as it defines the set
    of devices, their interfaces, and the cabling-links that connect the
    device-interfaces.

    Attributes
    ----------
    name: str
        The topology name as defined by the Designer.  This name is typically
        the same name as the Design name; but it does not need to be.  This
        choice is up to the Designer.

    cabling: CableByCableId
        The cabling instance used to manage the relationship of the connected
        device interfaces.
    """

    def __init__(
        self, topology_name: str, feature_name: Optional[str] = "topology", **kwargs
    ):
        # The cabling must be created first becasue the add_devices, which is
        # called by the superclass constructor, uses cabling

        self.cabling = CableByCableId(name=topology_name)

        # set up the design service with the User provided service name

        super(TopologyDesignFeature, self).__init__(feature_name=feature_name, **kwargs)
        self.registry_add(name=topology_name, obj=self)
        self.topology_name = topology_name

        self.check_collections = copy(self.__class__.CHECK_COLLECTIONS)

    def add_devices(self, *devices: Device):
        super(TopologyDesignFeature, self).add_devices(*devices)
        self.cabling.add_devices(*devices)

    def build(self):
        self.cabling.build()

    def validate(self):
        # TODO: put cabling validate here.
        pass


TopologyFeatureLike = TypeVar(
    "TopologyFeatureLike", TopologyDesignFeature, DesignFeature
)
