import json

from pydantic import BaseModel, Field, ValidationError

from netcad.logger import get_logger
from .device import DeviceKindRegistry, Device


class DeviceDecl(BaseModel):
    alias: str = Field(description="User-friendly name for the device")
    profile: str = Field(description="Indentifies the Device subclass")
    hostname: str = Field(description="Hostname or IP address of the device")
    primary_ip: str | None = Field(None, description="Primary IP address of the device")

    # identifies the list of interface alias->if_name mappings that this
    # device will be using.
    interface_maps: list[str] | None = Field(default_factory=list)


def build_devices_from_decl(
    device_decls: list[dict],
    interface_map_decls: list[dict],
) -> dict[str, Device]:
    log = get_logger()
    devices = dict()
    error_c = 0

    for dev_cfg in device_decls:
        try:
            dev_decl = DeviceDecl.parse_obj(dev_cfg)
        except ValidationError as exc:
            log.error(
                "Error parsing device declaration: %s",
                json.dumps(exc.errors(), indent=3),
            )
            error_c += 1
            continue

        if not (kind_cls := DeviceKindRegistry.get(dev_decl.profile)):
            log.error("Unknown device kind '%s'", dev_decl.profile)
            error_c += 1
            continue

        dev: Device
        dev = kind_cls(name=dev_decl.hostname, alias=dev_decl.alias)
        for if_map in dev_decl.interface_maps:
            if_map_cfg = interface_map_decls[if_map]
            dev.interfaces_map.update(zip(if_map_cfg.values(), if_map_cfg.keys()))

        if dev_decl.primary_ip:
            dev.primary_ip = dev_decl.primary_ip

        devices[dev.alias] = dev

    if error_c:
        raise RuntimeError("Errors loading device configurations, aborting.")

    return devices
