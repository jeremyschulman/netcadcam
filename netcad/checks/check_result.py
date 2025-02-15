#  Copyright (c) 2022 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Any, List, TypeVar, Generic
import typing

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import Field, field_validator, RootModel, BaseModel
from pydantic._internal._model_construction import ModelMetaclass
from pydantic_core.core_schema import ValidationInfo

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from .check import Check
from .check_status import CheckStatus, CheckStatusFlag
from .check_result_log import CheckResultLogs

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["CheckResult", "CheckResultList", "CheckResultsCollection"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class MetaCheckResult(ModelMetaclass):
    """
    This metaclass is used to default-factory the 'measurement' instance to the
    specific class-type designated in the measurement annotation.  This is done
    for a better DX so that the developer does not need to explicity
    instantiate the measurement prior to creating the check-result.
    """

    def __new__(mcs, name, bases, namespaces, **kwargs):
        if not (annots := namespaces.get("__annotations__")):
            return super().__new__(mcs, name, bases, namespaces, **kwargs)

        _field = "measurement"

        if (msrd_cls := annots.get(_field)) is None:
            if Generic not in bases:
                raise RuntimeError(
                    f"Missing {name}, required annotation for measurement field"
                )

        t_args = typing.get_args(msrd_cls)
        if t_args and t_args[0] == typing.Any:
            return super().__new__(mcs, name, bases, namespaces, **kwargs)

        annots[_field] = Optional[annots[_field]]
        namespaces[_field] = Field(default_factory=msrd_cls)

        new_type = super().__new__(mcs, name, bases, namespaces, **kwargs)
        return new_type


CheckT = TypeVar("CheckT", bound=Check)


class CheckResult(BaseModel, Generic[CheckT], metaclass=MetaCheckResult):
    """
    The CheckResult is the base class for all Design service specific
    check-result definitions.  Each design service *SHOULD* define check
    specific CheckResult classes that bind the speciific Meassurement class so
    that there is consistency for a given check-result across different vendor
    implementations of making the check.
    """

    status: CheckStatus = Field(CheckStatus.PASS)
    device: Device | str
    check: CheckT
    check_id: Optional[str] = Field(None)
    field: Optional[str] = Field(None)

    # even though the default-factory here is provided as dict, the use of the
    # metaclass will instantiate measurement as an instance of the measurement
    # type as annotated ;-)

    measurement: Optional[Any] = Field(
        default_factory=dict, description="The measurement from the DUT"
    )

    logs: CheckResultLogs = Field(
        default_factory=CheckResultLogs, description="Any logged by the DUT"
    )

    # -------------------------------------------------------------------------
    #                       Public Methods
    # -------------------------------------------------------------------------

    def measure(self, **kwargs):
        """
        The developer must call finalize once they have completed filling in
        the check result measurement.  Finalize "post-processes" the
        measurement results as compared to the check expectations.  During this
        processing the status of the check-result is set and check-result logs
        are created.

        Addition Parameters
        -------------------
        on_mismatch: Callable[[field, expected, measured], status]
            When provided by the Developer, this callback is used to allow them
            to examine the specific field difference. The callback can return a
            check status other than FAIL to indicate that the specific field
            mismatch is not to be logged as an error.

        Returns
        -------
        The check-result instance(self) for chaining purposes.
        """
        return _finalize_result(self, **kwargs)

    # -------------------------------------------------------------------------
    #                     Pydantic specific
    # -------------------------------------------------------------------------

    class Config:
        """
        Allow the Developer to add any additional fields to the pydantic object
        for their own usage.
        """

        arbitrary_types_allowed = True
        json_encoders = {CheckResultLogs: lambda log: log.data}

    # noinspection PyUnusedLocal
    @field_validator("check_id", mode="before")
    @classmethod
    def _save_tc_id(cls, value, values: ValidationInfo):
        return values.data["check"].check_id()

    # -------------------------------------------------------------------------
    #                       Public Methods
    # -------------------------------------------------------------------------

    def __hash__(self):
        """make hashable for dict key purposes"""
        return id(self)


# -----------------------------------------------------------------------------
#
#                            PRIVATE CODE BEGINS
#
# -----------------------------------------------------------------------------


def _finalize_result(result: CheckResult, **kwargs) -> CheckResult:
    """See the `finalized` method documentation above"""

    check = result.check
    expd = check.expected_results
    msrd = result.measurement

    # if the result status is already assigned to INFO, then do not do any
    # further processing on it.

    if result.status == CheckStatus.INFO:
        return result

    # -------------------------------------------------------------------------
    # if the check-result does not contain a measurement value, then this
    # condition indicates that the check failed because the "thing" to be
    # measured does not exist on the device.  This could be, for example a VLAN
    # that is expected on the device is not actually on the device, so that a
    # measurement could not be taken; FAIL.
    # -------------------------------------------------------------------------

    if not msrd:
        params = check.check_params
        result.status = CheckStatus.FAIL
        result.logs.FAIL(
            "missing",
            dict(
                params=params.dict() if params else None,
                expected=check.expected_results.dict(),
            ),
        )
        return result

    # -------------------------------------------------------------------------
    # Check for per-field mismatches on the measurement compared to expected.
    # -------------------------------------------------------------------------

    def mismatch_is_error(_field, _expded, _actual):
        """by default the field mismatch is a check failure"""
        return CheckStatus.FAIL

    on_mismatch = kwargs.get("on_mismatch") or mismatch_is_error

    # check to see if there are any field-mismatches
    mismatch_fields = set()
    check_status_flags = CheckStatusFlag.PASS

    for field in msrd.__fields__:
        m_field = getattr(msrd, field)

        if (e_field := getattr(expd, field, None)) is None:
            # extra data supplied by DUT
            result.logs.INFO(field, m_field)
            continue

        # if the fields are mismatched, then invoke the developer callback (or
        # default) to deteremine the state of the check-result for this field.
        field_status = CheckStatus.PASS

        if e_field != m_field:
            field_status = on_mismatch(field, e_field, m_field) or CheckStatus.FAIL
            field_status_flag = field_status.to_flag()
            check_status_flags |= field_status_flag
            if field_status != CheckStatus.SKIP:
                mismatch_fields.add(field)

        result.logs.log(field_status, field, {"expected": e_field, "measured": m_field})

    if mismatch_fields:
        setattr(result, "field", ", ".join(mismatch_fields))

    if check_status_flags & CheckStatusFlag.FAIL:
        result.status = CheckStatus.FAIL

    return result


CheckResultsCollection = List[CheckResult]


class CheckResultList(RootModel):
    root: Optional[List[CheckResult]] = Field(default_factory=list)
