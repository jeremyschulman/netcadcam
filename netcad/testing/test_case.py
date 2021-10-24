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

__all__ = ["TestCase"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


# disabling pycharm inspections because: https://youtrack.jetbrains.com/issue/PY-16760)

# noinspection PyUnresolvedReferences
class TestCase(BaseModel):
    """
    TestCase is a base abstract class used to contain the specifications for a
    testable service.

    Attributes
    ----------
    test_case: str, optional
        Uniquely identifies the type of the test case within the service.  If
        not provided, defaults to the test cases service name.

    test_params: BaseModel
        A pydantic model that defines the required test-case parameters that
        will be used by the testing system at audit/execution time.

    expected_results: BaseModel
        A pydantic model that defines the expected test-case results so that the
        testing system knows the "correct answer".
    """

    test_case: Optional[str]
    test_params: BaseModel
    expected_results: BaseModel

    def test_case_id(self) -> str:
        """
        Returns a humaized string form to identify the test case.  This value
        will be used in testing reports and testing engines that may need an ID
        like value.  pytest comest to mind.
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
        kwargs["exclude_none"] = True
        return super(TestCase, self).dict(**kwargs)
