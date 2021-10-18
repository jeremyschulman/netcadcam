import os
from pathlib import Path
import json


from functools import lru_cache


from netcad.config.envvars import Environment


@lru_cache()
def cache_load_device_type(product_model: str) -> dict:
    c_dir = Path(os.environ[Environment.NETCAD_CACHEDIR])
    dt_dir = c_dir.joinpath("device-types")
    pm_file = dt_dir.joinpath(f"{product_model}.json")
    return json.load(pm_file.open())
