# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from os import environ

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import loader, netcad_globals

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["init"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def init():
    """
    The netcad primary initialization function.
    """

    # load the contents of the User's netcad configuration file, uses either the
    # environment vairable, or the default value.

    loader.load(environ.get("NETCAD_CONFIGFILE"))
    project_dir = netcad_globals.g_netcad_project_dir
    loader.import_networks(root_path=project_dir.absolute())

    environ.setdefault(
        "NETCAD_CACHEDIR", str(project_dir.joinpath(".netcad").absolute())
    )
