# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple
import sys
from pathlib import Path
from setuptools import find_packages
from importlib import import_module

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import click

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.jinja2.env import get_env
from netcad.logger import get_logger
from netcad.config import loader
from netcad.cli.main import clig_build


# -----------------------------------------------------------------------------
# Exports (none)
# -----------------------------------------------------------------------------

__all__ = []

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@clig_build.command(name="configs")
@click.option(
    "-n", "--name", "hostnames", help="device hostname", required=True, multiple=True
)
@click.option(
    "--configs-dir",
    help="location to store configs",
    type=click.Path(path_type=Path, resolve_path=True, exists=True, writable=True),
    default="configs",
)
@click.option(
    "--console", "output_console", help="display output to console", is_flag=True
)
def cli_render(hostnames: Tuple[str], configs_dir: Path, output_console: bool):
    """Build device configuration files"""

    log = get_logger()
    loader.import_networks()

    # TODO: change this importing based on the .netcad/config.toml file.

    sys.path.insert(0, "..")
    pkg_list = find_packages()
    for pkg in pkg_list:
        import_module(pkg)

    device_objs = list()
    for each_name in hostnames:
        if not (dev_obj := Device.registry_get(name=each_name)):
            log.error(f"Device not found: {each_name}")
            return

        device_objs.append(dev_obj)

    template_dir = Path().absolute().joinpath(pkg_list[0], "templates")
    env = get_env(template_dirs=["/", template_dir])

    log.info(f"Building device configs into directory: {configs_dir.absolute()}")
    for dev_obj in device_objs:
        config_file = configs_dir.joinpath(dev_obj.name + ".cfg")
        log.debug(f"BUILD config for device {dev_obj.name}")

        template = dev_obj.get_template(env=env)
        config_text = template.render(device=dev_obj)

        log.info(f"SAVE: {dev_obj.name} config: {config_file.name}")
        with config_file.open("w+") as ofile:
            ofile.write(config_text)

        if output_console:
            print(config_text, end="")
