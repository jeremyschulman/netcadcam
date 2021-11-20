# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from types import ModuleType

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import netcad_globals
from netcad.init.loader import netcad_import_package

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["import_netcam_plugin"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def import_netcam_plugin() -> ModuleType:
    """
    This function imports the Python module defined in the User configuration
    file "netcam.package", and returns that module so that the Caller can use
    the `get_dut` function.

    Returns
    -------
    The plugin module as described.
    """
    if not (netcam_config := netcad_globals.g_config.get("netcam")):
        cfile = netcad_globals.g_netcad_config_file.absolute()
        raise RuntimeError(f'Configuration Missing: "netcam" section in file: {cfile}')

    if not (package := netcam_config.get("package")):
        cfile = netcad_globals.g_netcad_config_file.absolute()
        raise RuntimeError(
            f'Configuration Missing: "netcam.package" setting in file: {cfile}'
        )

    pl_mod = netcad_import_package(package)
    if not hasattr(pl_mod, "get_dut"):
        raise RuntimeError(
            f'Netcam plugin package "{package}" missing get_dut_type function'
        )

    return pl_mod
