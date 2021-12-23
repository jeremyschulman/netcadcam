# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["Check"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


# disabling pycharm inspections because: https://youtrack.jetbrains.com/issue/PY-16760)

# noinspection PyUnresolvedReferences
class Check(BaseModel):
    """
    Check is a base abstract class used to contain the specifications for a
    specific design network check.

    Attributes
    ----------
    check_type: str, optional
        Uniquely identifies the type of check within the service.  If
        not provided, defaults to the design service name.

    check_params: BaseModel
        A pydantic model that defines the required check parameters that will be
        used by the validator at audit/execution time.

    expected_results: BaseModel
        A pydantic model that defines the expected test-case results so that the
        testing system knows the "correct answer".
    """

    check_type: Optional[str]
    check_params: Optional[BaseModel]
    expected_results: BaseModel

    def check_id(self) -> str:
        """
        Returns a humaized string form to identify a specific check.  This value
        will be used in reports and validator engines that may need an ID like
        value.  pytest comest to mind.  For example, when checking "interfaces"
        the `check_id` would be the interface name.
        """
        raise NotImplementedError()

    # -------------------------------------------------------------------------
    #
    #                         BaseModel Overrides
    #
    # -------------------------------------------------------------------------

    def dict(self, **kwargs):
        """By default exclude any optional/None fields from serialization"""
        # TODO: may rethink this default.
        # kwargs["exclude_none"] = True
        return super(Check, self).dict(**kwargs)
