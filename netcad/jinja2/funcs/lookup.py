from typing import TYPE_CHECKING

import jinja2

from importlib import import_module

if TYPE_CHECKING:
    from netcad.device import Device


@jinja2.pass_context
def j2_func_lookup(ctx, module, var_attr):
    device: Device = ctx["device"]
    package = device.__class__.__module__.split(".")[0]
    mod_name = f"{package}.{module}"
    mod = import_module(mod_name)
    return getattr(mod, var_attr)
