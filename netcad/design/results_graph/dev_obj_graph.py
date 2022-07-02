#  Copyright (c) 2022 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from bidict import bidict
from igraph import Graph

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.design import Design

from .drg_typedefs import NodeObjIDMapT

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["DesignDevicesGraph"]


class DesignDevicesGraph:
    def __init__(self, design: Design):
        self.design = design
        self.graph = Graph(directed=True)
        self.nodeobj_map: NodeObjIDMapT = bidict()

        for dev_obj in design.devices.values():
            self.add_device(dev_obj)

    def add_device(self, device: Device):
        pass
