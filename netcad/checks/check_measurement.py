#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Union, List, Dict, Optional

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, Field
from pydantic._internal._model_construction import ModelMetaclass

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


class MetaMeasurement(ModelMetaclass):
    def __new__(mcs, name, bases, namespaces, **kwargs):
        annots = namespaces.get("__annotations__", {})
        cls = next((cls for cls in bases if cls.model_fields), None)

        if not cls and not annots:
            return super().__new__(mcs, name, bases, namespaces, **kwargs)

        if not annots:
            namespaces["__annotations__"] = annots

        if cls:
            for f_name, f_info in cls.model_fields.items():
                f_annot = f_info.annotation
                annots[f_name] = f_info.annotation
                namespaces[f_name] = Field(None)
                namespaces[f_name].annotation = Optional[f_annot]

        if annots:
            for f_name, f_annot in annots.items():
                namespaces[f_name] = Field(None)
                namespaces[f_name].annotation = Optional[f_annot]

        new_cls = super().__new__(mcs, name, bases, namespaces, **kwargs)
        return new_cls


class CheckMeasurement(BaseModel, metaclass=MetaMeasurement):  # extra=Extra.allow
    pass
