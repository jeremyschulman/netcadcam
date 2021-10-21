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


class TestCases(BaseModel):
    service: str  # the name definiting the service
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
    async def load(cls, testcase_dir: Path, service: str):
        async with aiofiles.open(cls.filepath(testcase_dir, service)) as infile:
            return parse_obj_as(cls, json.loads(await infile.read()))

    @classmethod
    def build(cls, obj: Any) -> "TestCases":
        raise NotImplementedError()
