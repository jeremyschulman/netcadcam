from importlib import import_module
from . import BUILTIN_TESTING_SERVICES


def on_init():

    for service in BUILTIN_TESTING_SERVICES:
        import_module(f"netcad.testing.{service}")
