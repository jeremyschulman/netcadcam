#  Copyright (c) 2025 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Dict, DefaultDict, Any, Type

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from bidict import bidict
import igraph

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.checks import CheckResult

CheckIDObjMapT = Dict[str, CheckResult]
CheckTypeCheckIdMapT = DefaultDict[str, CheckIDObjMapT]
ResultMapT = DefaultDict[Device, CheckTypeCheckIdMapT]
CheckResultT = Type[CheckResult]

GraphNode = igraph.Vertex
NodeObjIDMapT = bidict[Any, GraphNode]
