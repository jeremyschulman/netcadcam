from typing import Sequence, Optional, List, Set

from netcad.device import Device, DeviceNonExclusive
from netcad.logger import get_logger

__all__ = ["cli_config_filter_devices"]


def cli_config_filter_devices(
    device_objs: Sequence[Device], exclude_non_exclusive: Optional[bool] = False
) -> List[Device]:
    log = get_logger()
    device_objs = {dev for dev in device_objs if not dev.is_pseudo}

    if exclude_non_exclusive:
        devs_non_exclusive = {
            dev for dev in device_objs if isinstance(dev, DeviceNonExclusive)
        }
        non_exc_list = ", ".join(dev.name for dev in devs_non_exclusive)
        log.warning(f"SKIP, devices that are design non-exclusive: {non_exc_list}")
        device_objs -= devs_non_exclusive

    devs_no_primary_ip = {dev for dev in device_objs if not dev.primary_ip}
    no_primary_ip_names = ", ".join(dev.name for dev in devs_no_primary_ip)
    log.warning(
        f"SKIP, devices that are missing primary-IP assignment: {no_primary_ip_names}"
    )
    device_objs -= devs_no_primary_ip

    return sorted(device_objs)
