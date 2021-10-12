# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Any
from importlib import import_module

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import jinja2

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["get_env"]


@jinja2.pass_context
def j2_filter_render(ctx, obj: Any, to_render: str, **kwargs):
    meth = f"render_{to_render}"

    if call_meth := getattr(obj, meth, None):
        return call_meth(ctx, **kwargs)

    raise RuntimeError(f"object {str(obj)} does not support redner method: {meth}")


def j2_filter_ip_gateway(*vargs, **kwargs):
    return ""


@jinja2.pass_context
def j2_func_lookup(ctx, module, var_attr):
    device: Device = ctx["device"]
    package = device.__class__.__module__.split(".")[0]
    mod_name = f"{package}.{module}"
    mod = import_module(mod_name)
    return getattr(mod, var_attr)


def get_env(template_dirs):

    env = jinja2.Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        loader=jinja2.FileSystemLoader(template_dirs),
    )

    env.filters["render"] = j2_filter_render
    env.filters["ip_gateway"] = j2_filter_ip_gateway
    env.globals["lookup"] = j2_func_lookup

    return env
