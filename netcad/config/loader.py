from typing import Optional
import sys
from pathlib import Path
from importlib import import_module

import toml

from netcad.defaults import DEFAULT_NETCAD_CONFIG_FILE


def load(config_filepath: Optional[Path] = None):
    if not config_filepath:
        config_filepath = Path(DEFAULT_NETCAD_CONFIG_FILE)

    if not config_filepath.is_file():
        raise FileNotFoundError(str(config_filepath.absolute()))

    config_data = toml.load(config_filepath.open())
    return config_data


def network_importer(config: dict):
    sys.path.insert(0, ".")
    pkg_list = config["networks"]
    for pkg in pkg_list:
        import_module(pkg)
