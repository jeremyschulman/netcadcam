#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import asyncio
from inspect import iscoroutinefunction
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

    if not (design_decl := netcad_globals.g_netcad_designs.get(design_name)):
        raise RuntimeError(
            f'Missing design "{design_name}" definitions in config-file: '
        )

    design_pkg = design_decl.get("package")
    group_members = design_decl.get("group")

    if not group_members and not design_pkg:
        raise RuntimeError(
            f'Missing in "{design_name}": expected "package" defintion in config-file: '
            f"{netcad_globals.g_netcad_config_file}"
        )

    # if the User has defined an explicit package, then load the design as a sington.from
    if design_pkg:
        return load_design_singleton(
            design_name=design_name, pkg_name=design_pkg, design_decl=design_decl
        )

    # if here, then then the User selected a group that does not include a
    # package defined, which is the general case, and we load the design group
    # automatically.

    return load_design_group(
        group_name=design_name, group_members=group_members, design_config=design_decl
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

        # need to swap the use of alias as key for the name, since multiple
        # sites will have the same alias values; and that results in only one
        # (last) site.  doeh.  So use the device name as the key into the
        # devices dict for this use-case.

        devices = {d.name: d for alias, d in d_site_obj.devices.items()}
        group_design.devices.update(devices)

    return group_design


def load_design_singleton(design_name: str, pkg_name: str, design_decl: dict) -> Design:
    """
    Load a single design module, calling the `create_design` method.

    Parameters
    ----------
    design_name: str
        The name of the design as found in the User configuration file.

    pkg_name: str
        The package name in dotted-notation where the create_design function
        is located.

    design_decl: dict
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

    # ensure there is a design.config dictionary, that is initialized
    # with the description value from the config file.from

    design_decl.setdefault("config", {})
    design_decl["config"]["description"] = design_decl.get("description", "")

    design_inst = Design(name=design_name, config=design_decl["config"])

    # Execute the design function in the module if present.  If one is not
    # found, then this is a Designer error, and raise a Runtime exception.

    if hasattr(design_mod, "create_design") and callable(design_mod.create_design):
        try:
            if iscoroutinefunction(design_mod.create_design):
                design_inst = asyncio.run(design_mod.create_design(design_inst))
            else:
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
