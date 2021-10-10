from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from netcad.interface_profile import InterfaceProfile


class DeviceInterface(object):
    def __init__(
        self,
        name: str,
        profile: Optional["InterfaceProfile"] = None,
        used: Optional[bool] = True,
        desc: Optional[str] = "",
    ):
        self.name = name
        self.profile = profile
        self.used = used
        self.desc = desc

    def __repr__(self):

        if self.profile:
            return f"{self.name}:{self.profile.__class__.__name__}"

        if self.used is False:
            return "Unused"

        return f"{self.name}:{self.__class__.__name__}"
