#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, Field

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

    check_type: str
    expected_results: BaseModel
    check_params: Optional[BaseModel] = Field(None)

    def check_id(self) -> str:
        """
        Returns a humaized string form to identify a specific check.  This
        value will be used in reports and validator engines that may need an ID
        like value.  pytest comest to mind.  For example, when checking
        "interfaces" the `check_id` would be the interface name.
        """
        return self.check_type

    # -------------------------------------------------------------------------
    #
    #                         BaseModel Overrides
    #
    # -------------------------------------------------------------------------

    def dict(self, **kwargs):
        """By default, exclude any optional/None fields from serialization"""
        # TODO: may rethink this default.
        # kwargs["exclude_none"] = True
        return super(Check, self).dict(**kwargs)

    @classmethod
    def check_type_(cls):
        """Used to get the check_type value from the class declaration"""
        return cls.__fields__["check_type"].default
