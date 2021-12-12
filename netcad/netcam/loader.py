# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------
import os
from typing import Dict, Callable, Optional

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, Field

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


class NetcamTestingPluginConfig(BaseModel):
    package: str  # TODO use a module reference regular expression for validation
    get_dut: Callable
    config: Optional[Dict] = Field(default_factory=dict)
    env: Optional[Dict[str, str]] = Field(default_factory=dict)


NetcamTestingPluginCatalog = Dict[str, NetcamTestingPluginConfig]


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

    for pg_id, pg_item in enumerate(testing_plugins, start=1):

        cfg_ref = f"netam.test.{pg_id}"
        if not (modref := pg_item.get("package")):
            raise RuntimeError(f'Configuration missing "{cfg_ref}.package": {cfg_file}')

        if not (supported_os_names := pg_item.get("supports")):
            raise RuntimeError(
                f'Configuration missing "{cfg_ref}.supports": {cfg_file}'
            )

        try:
            pl_mod = loader.import_objectref(modref)
        except ModuleNotFoundError:
            raise RuntimeError(
                f'Testing package for "{cfg_ref}" module is not found/installed: {modref}'
            )

        if not (get_dut := getattr(pl_mod, "get_dut", None)):
            raise RuntimeError(f"{cfg_ref} module missing get_dut function")

        # if the netcad.toml plugin configuration contains an enviroment
        # section, then place the environment variables.

        if pg_cfg_env := pg_item.get("env"):
            for var_name, var_val in pg_cfg_env.items():
                os.environ[var_name] = var_val

        pg_item["get_dut"] = get_dut
        pg_cfg_obj = NetcamTestingPluginConfig.parse_obj(pg_item)

        for os_name in supported_os_names:
            netcad_globals.g_testing_plugins[os_name] = pg_cfg_obj

    return netcad_globals.g_testing_plugins
