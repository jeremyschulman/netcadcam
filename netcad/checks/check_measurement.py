#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Union, List, Dict, Optional
from itertools import filterfalse

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import pydantic
from pydantic import BaseModel, Extra

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#                              "Measurements"
# -----------------------------------------------------------------------------
#   A "measurement" is an object containing the values the DUT collection for a
#   specific "check" that are stored in the "check-result".
#
#   The measurement class is referenced by the specific "check-result" class
#   definition so that there is cohesion between what the check is expecting
#   and a well-defined schema for the expected measurements.  This is required
#   so that different implementations of the same check (for different network
#   OS vendors) have a well-defined and normalized structure for reporting the
#   measurement.
#
#   Generally speaking the measurement fields are the same as the check
#   expectation fields.  In some cases the measurement may contain additional
#   fields that are required or optional depending on the specific check in the
#   design service.
#
# -----------------------------------------------------------------------------

# !! order matters here, ensure bool is first
AnyMeasurementType = Union[bool, int, float, List, Dict, None, str]


class MetaMeasurement(pydantic.main.ModelMetaclass):
    def __new__(mcs, name, bases, namespaces, **kwargs):
        annotations = namespaces.get("__annotations__", {})

        for base in bases:
            annotations.update(base.__annotations__)

        for field in filterfalse(lambda _f: _f.startswith("__"), annotations):
            annotations[field] = Optional[annotations[field]]

            # if the field has a Field() designated, it will show in the
            # namespace dictionary.  Need to set the default to None so that it
            # is not required.
            if field_ns := namespaces.get(field):
                field_ns.default = None

        namespaces["__annotations__"] = annotations
        new_cls = super().__new__(mcs, name, bases, namespaces, **kwargs)
        return new_cls


class CheckMeasurement(BaseModel, extra=Extra.allow, metaclass=MetaMeasurement):
    pass
