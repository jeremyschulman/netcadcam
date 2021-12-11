# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Dict, Callable

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import netcad_globals, loader

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["import_netcam_plugin", "NetcamTestingPluginCatalog"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


NetcamTestingPluginCatalog = Dict[str, Callable]


def import_netcam_plugin() -> NetcamTestingPluginCatalog:
    """
    This function imports the Python module defined in the User configuration
    file "netcam.package", and returns that module so that the Caller can use
    the `get_dut` function.

    Returns
    -------
    The plugin module as described.
    """

    cfg_file = netcad_globals.g_netcad_config_file.absolute()

    try:
        testing_plugins: Dict = netcad_globals.g_config["netcam"]["test"]

    except KeyError:
        raise RuntimeError(f'Configuration "netcam.test" missing: {cfg_file}')

    for os_name, pg_cfg in testing_plugins.items():
        cfg_ref = f"netam.test.{os_name}.package"
        if not (modref := pg_cfg.get("package")):
            raise RuntimeError(f'Configuration missing "{cfg_ref}": {cfg_file}')

        try:
            pl_mod = loader.import_objectref(modref)
        except ModuleNotFoundError:
            raise RuntimeError(
                f'Testing package for "{cfg_ref}" module is not found/installed: {modref}'
            )

        if not (get_dut := getattr(pl_mod, "get_dut", None)):
            raise RuntimeError(f"{cfg_ref} module missing get_dut function")

        netcad_globals.g_testing_plugins[os_name] = get_dut

    return netcad_globals.g_testing_plugins
