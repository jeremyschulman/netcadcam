#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from netcad.plugins import NetcadPlugin


BUILTIN_PLUGINS = ["netcad.feats.topology", "netcad.feats.vlans"]


def init_netcad_builtin_plugins():
    for pg_item in BUILTIN_PLUGINS:
        pg_obj = NetcadPlugin(config=dict(name=pg_item, package=pg_item))
        pg_obj.load()
