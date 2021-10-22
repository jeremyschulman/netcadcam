from importlib import import_module


def on_init():
    import_module("netcad.testing.vlans")
    import_module("netcad.testing.lags")
