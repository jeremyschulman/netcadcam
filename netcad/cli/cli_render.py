import sys
from pathlib import Path
from setuptools import find_packages
from importlib import import_module

import click
import jinja2

from netcad.device import get_device, Device
from .main import cli


@jinja2.pass_context
def j2_filter_render(ctx, device: Device, to_render: str, **kwargs):
    meth = f"render_{to_render}"
    if call_meth := getattr(device, meth, None):
        return call_meth(ctx, **kwargs)

    raise RuntimeError(f"device does not support: {meth}")


def j2_filter_ip_gateway(*vargs, **kwargs):
    return ""


@jinja2.pass_context
def j2_func_lookup(ctx, module, var_attr):
    device: Device = ctx["device"]
    package = device.__class__.__module__.split(".")[0]
    mod_name = f"{package}.{module}"
    mod = import_module(mod_name)
    return getattr(mod, var_attr)


@cli.command(name="render")
@click.option("-h", "--host", "hostname", help="device hostname", required=True)
@click.pass_context
def cli_render(ctx: click.Context, hostname: str):
    """Render the configuration for a given device"""

    sys.path.insert(0, ".")
    pkg_list = find_packages()
    for pkg in pkg_list:
        import_module(pkg)

    if not (dev_obj := get_device(name=hostname)):
        ctx.fail(f"Device not found: {hostname}")
        return

    template_dir = Path().absolute().joinpath(pkg_list[0], "templates")

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(["/", template_dir]))

    env.filters["render"] = j2_filter_render
    env.filters["ip_gateway"] = j2_filter_ip_gateway
    env.globals["lookup"] = j2_func_lookup

    template = env.get_template(name=str(dev_obj.template_file))

    config_text = template.render(device=dev_obj)
    print(config_text)
