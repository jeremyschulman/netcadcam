from pydantic.dataclasses import dataclass


@dataclass()
class OriginDeviceTypeInterfaceSpec:
    if_name: str
    if_type: str
    if_type_label: str


class OriginDeviceType(object):
    def __init__(self, origin, origin_spec):
        self.origin = origin
        self.origin_spec = origin_spec

    def get_interface(self, if_name: str):
        raise NotImplementedError()
