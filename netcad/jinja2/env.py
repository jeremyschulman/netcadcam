#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

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

from . import j2_funcs
from . import j2_filters

from netcad.helpers import range_string

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
    "ipam_interface": j2_filters.j2_ipam_interface,
    "vlan_ranges": j2_filters.j2_vlans_id_list,
    "render": j2_filters.j2_render,
    "range_string": range_string,
}

_env_globals = {
    "lookup": j2_funcs.j2_func_lookup,
    "global_import": j2_funcs.j2_func_import,
    "ipam_get": j2_funcs.j2_func_ipam_get,
}


def get_env(template_dirs):

    env = jinja2.Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        loader=jinja2.FileSystemLoader(template_dirs),
        undefined=jinja2.StrictUndefined,
    )

    env.filters.update(_env_filters)
    env.globals.update(_env_globals)

    return env
