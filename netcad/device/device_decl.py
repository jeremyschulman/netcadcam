from pydantic import BaseModel, Field

from netcad.logger import get_logger
from .device import DeviceKindRegistry, Device


class DeviceDecl(BaseModel):
    alias: str
    kind: str
    hostname: str
    use_interface_maps: list[str] | None = Field(default_factory=list)
    primary_ip: str | None = Field(None)


def build_devices_from_config(
    device_configs: list[dict],
    interface_maps: list[dict],
) -> dict[str, Device]:
    log = get_logger()
    devices = dict()

    for dev_cfg in device_configs:
        dev_decl = DeviceDecl.parse_obj(dev_cfg)

        if not (kind_cls := DeviceKindRegistry.get(dev_decl.kind)):
            log.error("Unknown device kind '%s'", dev_decl.kind)
            continue

        dev: Device
        dev = kind_cls(name=dev_decl.hostname, alias=dev_decl.alias)
        for if_map in dev_decl.use_interface_maps:
            if_map_cfg = interface_maps[if_map]
            dev.interfaces_map.update(zip(if_map_cfg.values(), if_map_cfg.keys()))

        if dev_decl.primary_ip:
            dev.primary_ip = dev_decl.primary_ip

        devices[dev.alias] = dev

    return devices
