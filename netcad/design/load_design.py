#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List

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

    A design typically has a `package` definition that defines the location of
    the `create_desgin` function.  If the package definition exists, then load
    the design as a "singleton", meaning that the code will execute the
    create_design function located in the given package.

    A User can also define a design that is a group of other designs.  In this
    case the `group` definition is a list of other designs, each of which would
    be expected to have a `package` definition.

    Parameters
    ----------
    design_name: str
        The name of design as defined by the User in the netcad configuraiton
        file.  For example, if the configuration file contained a toplevel entry

            [[design]]
                name = "foobaz"

    Then `design_name` is foobaz.

    Returns
    -------
    The design instance associated with the design-name.
    """

    if not (design_config := netcad_globals.g_netcad_designs.get(design_name)):
        raise RuntimeError(
            f'Missing design "{design_name}" definitions in config-file: '
        )

    design_pkg = design_config.get("package")
    group_members = design_config.get("group")

    if not group_members and not design_pkg:
        raise RuntimeError(
            f'Missing in "{design_name}": expected "package" defintion in config-file: '
            f"{netcad_globals.g_netcad_config_file}"
        )

    # if the User has defined an explicit package, then load the design as a sington.from

    if design_pkg:
        return load_design_singleton(
            design_name=design_name, pkg_name=design_pkg, design_config=design_config
        )

    # if here, then then the User selected a group that does not include a
    # package defined, which is the general case, and we load the design group
    # automatically.

    return load_design_group(
        group_name=design_name, group_members=group_members, design_config=design_config
    )


def load_design_group(
    group_name: str, group_members: List[str], design_config: dict
) -> Design:
    """
    This function is used to load a design that is designated as a group such that
    all of the group members are loaded and the return design instance accounts
    for all devices across all of the group member designs.

    Parameters
    ----------
    group_name: str
        The design name as found in the User configuration file.

    group_members: List[str]
        The list of member designs that this group encompases.

    design_config: dict
        The design configuration dictionary for the User design-group.

    Returns
    -------
    Design representing the collection of all devices in the groups of designs.
    """

    group_design = Design(name=group_name, config=design_config.get("config"))
    group_design.group = group_members

    for design_name in group_members:
        d_site_obj = load_design(design_name=design_name)
        group_design.devices.update(d_site_obj.devices)

    return group_design


def load_design_singleton(design_name: str, pkg_name: str, design_config: dict):
    """
    Load a single design module, calling the `create_design` method.

    Parameters
    ----------
    design_name: str
        The name of the design as found in the User configuration file.

    pkg_name: str
        The package name in dotted-notation where the create_design function
        is located.

    design_config: dict
        The dict instance of the design as found in the User configuration.  This
        is the entire body contents of the [[design]] block associated with
        the design-name.

    Returns
    -------
    Design instance
    """

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

    design_inst = Design(name=design_name, config=design_config.get("config"))

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
