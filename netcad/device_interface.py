from typing import Optional, TYPE_CHECKING
import re

if TYPE_CHECKING:
    from netcad.interface_profile import InterfaceProfile

_re_find_numbers = re.compile(r"\d+")


class DeviceInterface(object):
    def __init__(
        self,
        name: str,
        profile: Optional["InterfaceProfile"] = None,
        used: Optional[bool] = True,
        desc: Optional[str] = "",
    ):
        self.name = name
        self.port_numbers = tuple(map(int, _re_find_numbers.findall(name)))
        self.profile = profile
        self.used = used
        self.desc = desc

    # @property
    # def profile(self):
    #     return self._profile
    #
    # @profile.setter
    # def profile(self, assgined: InterfaceProfile):
    #     self._profile = assgined
    #     self._profile.if_name = self.name

    def __repr__(self):

        if self.profile:
            return f"{self.name}:{self.profile.__class__.__name__}"

        if self.used is False:
            return "Unused"

        return f"{self.name}:{self.__class__.__name__}"
