# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Iterable, AnyStr
from os import environ
from pathlib import Path
import json

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import aiofiles

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------


class Origin(object):
    def __init__(self):
        self.cache_dir = Path(environ["NETCAD_CACHEDIR"])

    @staticmethod
    async def save_file(filepath: Path, content):
        async with aiofiles.open(filepath.absolute(), "w+") as ofile:
            await ofile.write(json.dumps(content, indent=3))

    async def get_device_types(self, product_models: Iterable[AnyStr]):
        raise NotImplementedError()
