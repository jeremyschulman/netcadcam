from pydantic import BaseModel

# disabling pycharm inspections because: https://youtrack.jetbrains.com/issue/PY-16760)


# noinspection PyUnresolvedReferences
class TestCase(BaseModel):
    """
    TestCase is a base abstract class used to contain the specifications for a
    testable service.

    Attributes
    ----------
    test_case: str
        Uniquely identifies the type of the test case within the service.

    device: str
        The device hostname value

    test_params: BaseModel
        A pydantic model that defines the required test-case parameters that
        will be used by the testing system at audit/execution time.

    expected_results: BaseModel
        A pydantic model that defines the expected test-case results so that the
        testing system knows the "correct answer".
    """

    test_case: str
    device: str
    test_params: BaseModel
    expected_results: BaseModel

    def test_case_id(self) -> str:
        """Returns a humaized string form to identify the test case"""
        raise NotImplementedError()
