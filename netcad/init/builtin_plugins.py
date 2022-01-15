#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from netcad.plugins import NetcadPlugin


BUILTIN_PLUGINS = [dict(name="netcad.vlans", package="netcad.vlans")]


def init_netcad_builtin_plugins():
    for pg_item in BUILTIN_PLUGINS:
        pg_obj = NetcadPlugin(config=pg_item)
        pg_obj.load()
