from typing import Literal
from pydantic import BaseModel


class DesignServiceCheck(BaseModel):
    status: Literal["PASS", "FAIL"] = "PASS"

    def check(self):
        pass

    def ok(self) -> bool:
        self.check()
        return self.status == "PASS"

    def details(self):  # noqa
        return None

    def __bool__(self) -> bool:
        return self.ok()

    def __hash__(self):
        return id(self)
