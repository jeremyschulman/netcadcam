#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+
#  see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Iterable
import re
from itertools import chain
from os.path import expandvars

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from first import first
import jinja2
import datetime

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from . import j2_filters

from netcad.helpers import range_string

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["get_env", "expand_templates_dirs"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

_env_filters = {
    "ipam_interface": j2_filters.j2_ipam_interface,
    "vlan_ranges": j2_filters.j2_vlans_id_list,
    "render": j2_filters.j2_render,
    "startswith": lambda obj, pf: obj.startswith(pf),
    "range_string": range_string,
}


def now(strfmt: str = None) -> datetime.datetime | str:
    dt = datetime.datetime.now()
    return dt if not strfmt else dt.strftime(strfmt)


# class RelativeEnviornment(jinja2.Environment):
#     def get_template(self, name: str, parent=None, globals_=None) -> jinja2.Template:
#         if name.endswith("lawo_macros.jinja2"):
#             breakpoint()
#             x = 1
#
#         return super().get_template(name, parent, globals_)
#
#
# class RelativeFilesystemLoader(jinja2.FileSystemLoader):
#     def get_source(self, environment: jinja2.Environment, template: str):
#         if template.endswith("lawo_macros.jinja2"):
#             breakpoint()
#             x = 1
#
#         return super().get_source(environment, template)


def get_env(template_dirs):

    env = jinja2.Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        loader=jinja2.FileSystemLoader(template_dirs),
        undefined=jinja2.StrictUndefined,
    )

    env.filters.update(_env_filters)
    env.globals["now"] = now

    return env


_attr_re = re.compile(
    r"@{(?P<bname>[a-z\d_]+)}" r"|" r"@(?P<name>[^{][a-z_\d]+)", flags=re.IGNORECASE
)


def expand_templates_dirs(paths: Iterable[str], obj: object) -> List[str]:

    # expand enviornment variables in the path strings, if any.
    paths = [expandvars(path) for path in paths]

    # if the path strings do not contain any attribute (@) markers, then return
    # the list of paths now.

    if not any(path for path in paths if "@" in path):
        return paths

    # otherwise, find the set of attributes referenced in all the paths
    attr_list = set()
    for path in paths:
        this = filter(len, chain.from_iterable(_attr_re.findall(path)))
        attr_list.update(this)

    # extract the attribute-values from the passed object, presumed to be a
    # Device instance.

    attr_name: str
    attr_sub = {attr_name: str(getattr(obj, attr_name)) for attr_name in attr_list}

    # replace each instance of the attribute name with the attribute value.
    def repl_fun(_mo):
        return attr_sub[first(_mo.groups())]

    return [_attr_re.sub(repl_fun, path) for path in paths]
