from functools import wraps

from netcad.logger import get_logger
from netcad.netcam.dev_config import AsyncDeviceConfigurable


def temp_file(func):
    @wraps(func)
    async def __call__(dev_cfg: AsyncDeviceConfigurable, **kwargs):
        log = get_logger()
        name = dev_cfg.device.name
        log.info(f"{name}: copy config-file to device ...")
        raise_exc = None

        try:
            await dev_cfg.file_put()
        except Exception as exc:
            log.error(f"{name}: failed to copy file, aborting: {str(exc)}")
            return

        try:
            await func(dev_cfg, **kwargs)

        except Exception as exc:
            raise_exc = exc

        finally:
            log.info(f"{name}: remove copied config-file ...")
            await dev_cfg.file_delete()

        if raise_exc:
            raise raise_exc

    return __call__
