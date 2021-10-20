from pydantic import BaseModel


class TestCase(BaseModel):
    test_case: str  # The name of the test-case
    device: str  # The name of the device to be tested
    test_params: dict  # dictionary of test parameters, specific to test-case
    expected_results: dict  # expected test results for comparison pass/fail

    def test_case_id(self):
        raise NotImplementedError()
