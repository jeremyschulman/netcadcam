#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from types import ModuleType
from importlib import import_module

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["netcad_import_package"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def netcad_import_package(pkg_name: str) -> ModuleType:
    """
    This function will import the module as defined by the `pkg_name` value.
    This name originates in the netcad configuration file and could be one
    cases.  The first case is the package name referrs to an actual module file.
    The second case is that the package name referrs to an attribute within a
    package module.

    Parameters
    ----------
    pkg_name:
        The package name, as providing in standard Python dotted notation.

    Returns
    -------
    The module loaded.
    """

    # try to import the package name as given.  If the package name as given is
    # not found then we will try another approach.  The package name could be
    # given as an import reference within another file, for example "import foo
    # as bar" and the package name as given references "bar".  In this case the
    # direct import_module will fail resulting in a ModuleNotFound Error.
    try:
        return import_module(pkg_name)
    except ModuleNotFoundError as exc:
        if exc.name != pkg_name:
            raise RuntimeError(
                f"Failed to load {pkg_name} due to missing dependency: {exc.name}"
            )

        # otherwise pass

    # Try splitting the package as given into the package and then an attribute
    # within that module.  This will handle the case described above.

    try:
        from_pkg, design_name = pkg_name.rsplit(".", 1)
    except ValueError as exc:
        import traceback

        tb_data = traceback.format_tb(exc.__traceback__)
        raise RuntimeError(f"Failed to load package: {pkg_name}: {tb_data}")

    return getattr(import_module(from_pkg), design_name)
