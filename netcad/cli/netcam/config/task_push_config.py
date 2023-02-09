from pathlib import Path
from datetime import timedelta

from netcad.logger import get_logger
from netcad.netcam.dev_config import AsyncDeviceConfigurable
from .staged_config import SCPStagedConfig

_OK_ = "[green]OK:[/green]"
_CHANGED_ = "[blue]CHANGED:[/blue]"
_FAIL_ = "[red]FAIL:[/red]"


async def push_device_config(dev_cfg: AsyncDeviceConfigurable, timeout: timedelta):
    log = get_logger()

    name = dev_cfg.device.name

    # -------------------------------------------------------------------------
    # Stage the change
    # -------------------------------------------------------------------------

    scp_cfg = SCPStagedConfig(
        dev_cfg=dev_cfg, config_file=Path(dev_cfg.config_dir.joinpath(name + ".cfg"))
    )

    if await scp_cfg.stage():
        log.info(f"{name}: {_OK_} config-load passes")
    else:
        log.warning(f"{name}: {_FAIL_} config-load failed")

    # -------------------------------------------------------------------------
    # if there are not any config differences after the stage, then we let the
    # User know, and we are done with the push process.
    # -------------------------------------------------------------------------

    if not scp_cfg.config_diff:
        log.info(f"{name}: {_OK_} no config changes to make")
        await scp_cfg.abort()
        return

    # -------------------------------------------------------------------------
    # Commit the changes, which saves to startup as well
    # -------------------------------------------------------------------------

    log.info(f"{name}: commiting config with rollback timer {str(timeout)} ...")

    if await scp_cfg.commit(rollback_timeout=timeout):
        log.info(f"{name}: {_CHANGED_} config changed and saved to startup")
    else:
        log.warning(f"{name}: {_FAIL_} config failed to commit due to reachability")
