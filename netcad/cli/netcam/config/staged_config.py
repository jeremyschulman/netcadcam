from pathlib import Path
from datetime import timedelta

from asyncssh import SFTPError
import aiofiles
import aiofiles.os

from netcad.logger import get_logger
from netcad.device import DeviceNonExclusive
from netcad.netcam.dev_config import AsyncDeviceConfigurable


class SCPStagedConfig:
    def __init__(self, dev_cfg: AsyncDeviceConfigurable, config_file: Path):
        self.dev_cfg = dev_cfg
        self.device = dev_cfg.device
        self.name = self.device.name
        self.config_file = config_file
        self.diff_file: Path | None = None
        self.config_diff: str | None = None
        self.errmsg: str | None = None

    async def stage(self) -> bool:
        log = get_logger()

        basecfg_name = self.config_file.name

        # load the design config from the local filesystem so that we can load it
        # onto the device.

        log.info(
            f"{self.name}: Loading configuration for check puroses only: id={self.dev_cfg.config_id}"
        )

        # if the device is not exclusively management by netcadcam, then
        # load the config using a "merge".  If it is exclusively management
        # by netcadcam the load the config using a "replace" opertation.

        replace = not isinstance(self.device, DeviceNonExclusive)

        load_failed = False
        try:
            await self.dev_cfg.scp_config(self.config_file, dst_filename=basecfg_name)

        except OSError as exc:
            log.error(f"{self.name}: local file access failed: {str(exc)}")
            load_failed = True

        except SFTPError as exc:
            log.error(f"{self.name}: SCP failed: {str(exc)}")
            load_failed = True

        if load_failed:
            log.warning(f"{self.name}: aborting config-check")
            return False

        try:
            await self.dev_cfg.load_scp_file(filename=basecfg_name, replace=replace)
        except Exception as exc:
            log.error(f"{self.name}: config-load failed: {str(exc)}")
            return False

        try:
            self.config_diff = await self.dev_cfg.diff_config()

        except Exception as exc:
            log.error(f"{self.name}: diff-config failed: {str(exc)}")
            await self.dev_cfg.abort_config()
            return False

        diffs_dir = self.dev_cfg.config_dir / "diffs"
        await aiofiles.os.makedirs(diffs_dir, exist_ok=True)
        self.diff_file = diffs_dir / basecfg_name

        async with aiofiles.open(self.diff_file, "w+") as ofile:
            await ofile.write(self.config_diff)
            log.info(f"{self.name}: config-diff saved to: {ofile.name}")

        return True

    async def commit(self, timeout: timedelta):
        await self.dev_cfg.save_config(timeout=timeout)
        await self.scp_cleanup()

    async def abort(self):
        await self.dev_cfg.abort_config()
        await self.scp_cleanup()

    async def scp_cleanup(self):
        await self.dev_cfg.delete_scp_file(self.config_file.name)
