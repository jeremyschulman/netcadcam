# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional, Any
from pathlib import Path
import json

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, Field, parse_obj_as
import aiofiles

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from . import TestCase


# noinspection PyUnresolvedReferences
class TestCases(BaseModel):
    """
    Attributes
    ----------
    service: str
        The name of the testing service, "cabling" for example, that allows the
        Designer to register/retrieve test-cases by name.

    device: str
        The name of the device for which the tests will be executed against by
        the testing engine.  The `device` attribute could also be used as a
        "device under test" (DUT) or "system under test" (SUT) depending on the
        specific use of the test cases.

    exclusive: bool, optional
        When True (default) indicates that the list of tests are the exclude set
        of items that should be present on the device/dut.  For example if the
        "interfaces" test-cases is exclusive, and the device has an interface
        not in the tests list, then an exception will be raised by the testing
        engine.

    tests: List[TestCases], optional
        The list of specific test cases that will be executed by the testing
        engine.

    """

    service: str
    device: str
    exclusive: Optional[bool] = Field(default=True)
    tests: Optional[List[TestCase]] = Field(default_factory=list)

    @staticmethod
    def filepath(testcase_dir: Path, service: str) -> Path:
        return testcase_dir.joinpath(f"{service}.json")

    async def save(self, testcase_dir: Path):
        async with aiofiles.open(
            self.filepath(testcase_dir, self.service), "w+"
        ) as ofile:
            await ofile.write(json.dumps(self.dict(), indent=3))

    @classmethod
    def get_service_name(cls):
        return cls.__dict__["__fields__"]["service"].default

    @classmethod
    async def load(cls, testcase_dir: Path):
        async with aiofiles.open(
            cls.filepath(testcase_dir, cls.get_service_name())
        ) as infile:
            return parse_obj_as(cls, json.loads(await infile.read()))

    @classmethod
    def build(cls, obj: Any) -> "TestCases":
        raise NotImplementedError()
