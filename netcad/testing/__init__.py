from .test_case import TestCase
from .test_results import TestPass, TestFailed
from .test_cases import TestCases
from .testing_registry import testing_service, TestingServices

BUILTIN_TESTING_SERVICES = frozenset(
    ("device", "interfaces", "cabling", "lags", "mlags", "transceivers", "vlans")
)

DEFAULT_TESTING_SERVICES = BUILTIN_TESTING_SERVICES - {"mlags"}
