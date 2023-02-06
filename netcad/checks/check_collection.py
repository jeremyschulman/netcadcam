#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import sys
from typing import List, Optional, Any, Type, Dict
from typing import TYPE_CHECKING
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

from . import Check, CheckResult

if TYPE_CHECKING:
    from netcad.design import DesignService


# noinspection PyUnresolvedReferences
class CheckCollection(BaseModel):
    """
    Attributes
    ----------
    name: str
        The name of the check collection, "cabling" for example, that
        allows the Designer to register/retrieve checks by name.

    device: str
        The name of the device for which the tests will be executed against by
        the testing engine.  The `device` attribute could also be used as a
        "device under test" (DUT) or "system under test" (SUT) depending on the
        specific use of the test cases.

    exclusive: bool, optional
        When True (default) indicates that the list of tests are to exclude set
        of items that should be present on the device/dut.  For example if the
        "interfaces" test-cases is exclusive, and the device has an interface
        not in the tests list, then an exception will be raised by the testing
        engine.

    checks: List[Checks], optional
        The list of specific checks that will be executed by the validation
        engine.
    """

    name: str
    device: str
    exclusive: Optional[bool] = Field(default=True)
    checks: Optional[List[Check]] = Field(default_factory=list)

    @staticmethod
    def filepath(testcase_dir: Path, service: str) -> Path:
        return testcase_dir.joinpath(f"{service}.json")

    async def save(self, testcase_dir: Path):
        async with aiofiles.open(self.filepath(testcase_dir, self.name), "w+") as ofile:
            await ofile.write(json.dumps(self.dict(), indent=3))

    @classmethod
    def get_name(cls):
        return cls.__dict__["__fields__"]["name"].default

    @classmethod
    async def load(cls, testcase_dir: Path):
        async with aiofiles.open(cls.filepath(testcase_dir, cls.get_name())) as infile:
            return parse_obj_as(cls, json.loads(await infile.read()))

    @classmethod
    def build(cls, obj: Any, design_service: "DesignService") -> "CheckCollection":
        raise NotImplementedError()

    # -------------------------------------------------------------------------
    # Time for some introspection ...
    #
    # When a Developer creates a python module with a CheckCollection, this
    # bit of code will introspect that module to learn about what Check
    # and CheckResult classes are defined.  This code will then keep an
    # internal mapping of the check-type (str-name) to the class definitions
    # so that we can parse these JSON payloads into objects later.
    # -------------------------------------------------------------------------

    _check_results_type_map: Dict[str, Type[CheckResult]] = dict()

    @classmethod
    def parse_result(cls, result: dict) -> CheckResult:
        """
        Given the result in the form of a dictionary object, cover it to the
        associated CheckResult instance
        """

        # if the body contains a 'check' field, then this is a CheckResult
        # payload.  We need to look at the inner payload to find the check-type
        # value.

        if (check := result.get("check")) is None:
            raise ValueError('Required "check" missing in result')

        if (check_type := check.get("check_type")) is None:
            raise ValueError('Required "check_type" missing in result')

        if (cls_type := cls._check_results_type_map.get(check_type)) is None:
            raise ValueError(
                f"This check collection does not have bound check-type: {check_type}"
            )

        return cls_type.parse_obj(result)

    def __init_subclass__(cls, **kwargs):
        mod = sys.modules.get(cls.__module__)

        if not (mod_all := getattr(mod, "__all__", None)):
            raise RuntimeError(f"Required __all__ missing from module {cls.__module__}")

        def is_result_type(_t):
            try:
                return issubclass(_t, CheckResult)
            except TypeError:
                return False

        exports = filter(is_result_type, map(mod.__dict__.get, mod_all))
        for each in exports:
            if (check_field := each.__fields__.get("check")) is None:
                raise RuntimeError(f'Required "check" missing from {str(each)}')

            check_type_value = check_field.type_.__fields__["check_type"].default
            if not check_type_value:
                raise RuntimeError(f'Required "check_type" missing from: {str(each)}')

            cls._check_results_type_map[check_type_value] = each


CheckCollectionT = Type[CheckCollection]
