# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Dict, DefaultDict, Any

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from bidict import bidict

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.checks import CheckResult


CheckIDObjMapT = Dict[str, CheckResult]
CheckTypeCheckIdMapT = DefaultDict[str, CheckIDObjMapT]
ResultMapT = DefaultDict[Device, CheckTypeCheckIdMapT]

GraphNodeID = int
NodeObjIDMapT = bidict[Any, GraphNodeID]
