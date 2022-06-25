#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional, Any
import typing
import types

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import pydantic
from pydantic import validator, BaseModel, Field

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.checks.check import Check

from .check_status import CheckStatus


# -----------------------------------------------------------------------------
# Check Result Base Class
# -----------------------------------------------------------------------------


class MetaCheckResult(pydantic.main.ModelMetaclass):
    def __new__(mcs, name, bases, namespaces, **kwargs):
        _field = "measurement"
        annots = namespaces.get("__annotations__", {})

        # orig_bases = namespaces.get("__orig_bases__", {})
        # if name == 'PTPServiceCheckResult':
        #     breakpoint()
        #     x=1

        if (msrd_cls := annots.get(_field)) and (not namespaces.get(_field)):
            if isinstance(msrd_cls, types.UnionType):
                msrd_cls, _ = typing.get_args(msrd_cls)
            namespaces[_field] = Field(default_factory=msrd_cls)

        return super().__new__(mcs, name, bases, namespaces, **kwargs)


class CheckResult(BaseModel, metaclass=MetaCheckResult):
    status: CheckStatus = Field(CheckStatus.PASS)
    device: Device
    check: Check
    check_id: Optional[str]
    field: Optional[str]

    # The mesurement attribute is expected to be a BaseModel subclassed from
    # the Check expected_results BaseModel.  If there are no measurements it
    # means that the "thing" being checked by the DUT does not exist.

    measurement: Optional[Any] = Field(
        default_factory=dict, description="The measurement from the DUT"
    )

    logs: List = Field(default_factory=list, description="Any logged by the DUT")

    # noinspection PyUnusedLocal
    @validator("check_id", always=True)
    def _save_tc_id(cls, value, values: dict):
        return values["check"].check_id()

    class Config:
        arbitrary_types_allowed = True

    @staticmethod
    def log_result(result: dict):
        return result

    def finalize(self, **kwargs):
        return _finalize_result(self, **kwargs)


def _finalize_result(result: CheckResult, **kwargs) -> CheckResult:

    check = result.check
    expd = check.expected_results
    msrd = result.measurement

    def mismatch_is_error(_field, _expded, _actual):
        return CheckStatus.FAIL

    on_mismatch = kwargs.get("on_mismatch") or mismatch_is_error

    if not msrd:
        params = check.check_params
        result.status = CheckStatus.FAIL
        result.logs.append(
            [
                "ERROR",
                "missing",
                dict(
                    params=params.dict() if params else None,
                    expected=check.expected_results.dict(),
                ),
            ]
        )
        return result

    # check to see if there are any field-mismatches
    mismatches = []
    for field in msrd.__fields__:

        m_field = getattr(msrd, field)

        if (e_field := getattr(expd, field, None)) is None:
            # extra data supplied by DUT
            result.logs.append(["INFO", field, m_field])
            continue

        if not (matched := (e_field == m_field)):
            status = on_mismatch(field, e_field, m_field) or CheckStatus.FAIL

            if status != CheckStatus.FAIL:
                continue

            mismatches.append(field)

        result.logs.append(
            [
                ["ERROR", "OK"][matched],
                field,
                {"expected": e_field, "measured": m_field},
            ]
        )

    if mismatches:
        setattr(result, "field", ", ".join(mismatches))
        result.status = CheckStatus.FAIL

    return result
