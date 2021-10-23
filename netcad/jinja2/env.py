# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import jinja2

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .filters import vlan_filters
from .filters.render import j2_filter_render
from .filters import ipam
from .funcs.lookup import j2_func_lookup

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["get_env"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

_env_filters = {
    "ipam_interface": ipam.ipam_interface,
    # "vlans": vlan_filters.j2_filter_vlans,
    "vlan_ranges": vlan_filters.j2_filter_vlans_id_list,
    "render": j2_filter_render,
}

_env_globals = {"lookup": j2_func_lookup}


def get_env(template_dirs):

    env = jinja2.Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        loader=jinja2.FileSystemLoader(template_dirs),
    )

    env.filters.update(_env_filters)
    env.globals.update(_env_globals)

    return env
