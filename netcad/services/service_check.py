from typing import ClassVar
from pydantic import BaseModel


class DesignServiceCheck(BaseModel):
    check_type: ClassVar[str] = "service_check"
    ok: bool = True

    def details(self):  # noqa
        return None

    def __bool__(self) -> bool:
        return self.ok

    def __hash__(self):
        return id(self)
