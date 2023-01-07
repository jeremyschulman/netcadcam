#  Copyright (c) 2023 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# Systeme Imports
# -----------------------------------------------------------------------------

from typing import TypeVar
from copy import copy

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.design.design_service import DesignService

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .mlag_cabling import CableMLagsByCableId

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["MLagDesignService", "MLagServiceLike"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class MLagDesignService(DesignService, registry_name="mlags"):
    CHECK_COLLECTIONS = []  # none for now

    def __init__(self, service_name: str, **kwargs):

        # The cabling must be created first becasue the add_devices, which is
        # called by the superclass constructor, uses cabling

        self.cabling = CableMLagsByCableId(name=service_name)

        # set up the design service with the User provided service name

        super(MLagDesignService, self).__init__(service_name=service_name, **kwargs)
        self.registry_add(name=service_name, obj=self)
        self.check_collections = copy(self.__class__.CHECK_COLLECTIONS)

    def add_devices(self, *devices):
        super(MLagDesignService, self).add_devices(*devices)
        self.cabling.add_devices(*devices)

    def build(self):
        self.cabling.build()

    def validate(self):
        pass


MLagServiceLike = TypeVar("MLagServiceLike", MLagDesignService, DesignService)
