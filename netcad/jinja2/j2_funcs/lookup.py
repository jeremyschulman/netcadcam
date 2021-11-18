from typing import TYPE_CHECKING

import jinja2

from importlib import import_module

if TYPE_CHECKING:
    from netcad.device import Device

__all__ = ["j2_func_lookup", "j2_func_import"]


@jinja2.pass_context
def j2_func_lookup(ctx, module, var_attr):
    device: Device = ctx["device"]
    package = device.__class__.__module__.split(".")[0]
    mod_name = f"{package}.{module}"
    mod = import_module(mod_name)
    return getattr(mod, var_attr)


def j2_func_import(from_package, import_target=None):
    mod = import_module(from_package)
    return mod if not import_target else getattr(mod, import_target)
