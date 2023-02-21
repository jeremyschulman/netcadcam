#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from functools import wraps

from netcad.logger import get_logger
from netcam.dcfg import AsyncDeviceConfigurable


def temp_file(func):
    @wraps(func)
    async def __call__(dev_cfg: AsyncDeviceConfigurable, **kwargs):
        log = get_logger()
        name = dev_cfg.device.name
        log.info(f"{name}: copy config-file to device ...")
        raise_exc = None

        try:
            await dev_cfg.setup()
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
            await dev_cfg.teardown()

        if raise_exc:
            raise raise_exc

    return __call__
