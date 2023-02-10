from netcad.netcam.dev_config import AsyncDeviceConfigurable
from .deco_temp_file import temp_file

_OK_ = "[green]OK:[/green]"
_CHANGED_ = "[blue]CHANGED:[/blue]"
_FAIL_ = "[red]FAIL:[/red]"


@temp_file
async def push_device_config(dev_cfg: AsyncDeviceConfigurable, rollback_timeout: int):
    await dev_cfg.config_push(rollback_timeout=rollback_timeout)
