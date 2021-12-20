# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import netcad_globals
from netcad.init import netcad_import_package
from .design import Design

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["load_design"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def load_design(design_name: str) -> Design:
    """
    This function loads the specific design by importing the related package and
    executes the `design` function.

    Parameters
    ----------
    design_name: str
        The name of design as defined by the User in the netcad configuraiton
        file.  For example, if the configuration file contained a toplevel entry
        "[design.foobaz]" then the `design_name` is "foobaz".

    Returns
    -------
    The design configuration dictionary after execution of the design function.
    """

    if not (design_config := netcad_globals.g_netcad_designs.get(design_name)):
        raise RuntimeError(
            f'Missing design "{design_name}" definitions in config-file: {netcad_globals.g_netcad_config_file}'
        )

    pkg_name = design_config["package"]

    try:
        design_mod = netcad_import_package(pkg_name)

    # If there is any exception during the importing of the module, that is a
    # coding error by the Developer, then we need to raise that so the CLI
    # output will dispaly the information to the User with the hopes that the
    # information will aid in debugging.

    except Exception as exc:
        rt_exc = RuntimeError(
            f'Failed to import design "{design_name}" from package: "{pkg_name}";\n'
            f"Exception: {str(exc)}",
        )
        rt_exc.__traceback__ = exc.__traceback__
        raise rt_exc

    if not design_mod:
        raise RuntimeError(f'Failed to import design "{design_name}"')

    design_inst = Design(name=design_name, config=design_config)

    # Execute the design function in the module if present.  If one is not
    # found, then this is a Designer error, and raise a Runtime exception.

    if hasattr(design_mod, "create_design") and callable(design_mod.create_design):
        try:
            design_inst = design_mod.create_design(design_inst)

        except Exception as exc:
            rt_exc = RuntimeError(
                f'Failed to execute "create_design" function for design: {design_name}: {str(exc)}'
            )
            rt_exc.__traceback__ = exc.__traceback__
            raise rt_exc

    else:
        raise RuntimeError(
            f'Missing expected "create_design" function in design module for: {design_name}'
        )

    design_inst.module = design_mod
    return design_inst
