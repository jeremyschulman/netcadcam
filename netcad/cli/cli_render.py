# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

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
from .cli_config import clig_config


@clig_config.command(name="render")
@click.option("-n", "--name", "hostname", help="device hostname", required=True)
@click.pass_context
def cli_render(ctx: click.Context, hostname: str):
    """Render the configuration for a given device"""

    sys.path.insert(0, ".")
    pkg_list = find_packages()
    for pkg in pkg_list:
        import_module(pkg)

    if not (dev_obj := Device.registry_get(name=hostname)):
        ctx.fail(f"Device not found: {hostname}")
        return

    template_dir = Path().absolute().joinpath(pkg_list[0], "templates")
    env = get_env(template_dirs=["/", template_dir])
    template = env.get_template(name=str(dev_obj.template_file))
    config_text = template.render(device=dev_obj)

    print(config_text)
