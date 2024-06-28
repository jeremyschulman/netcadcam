#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# Private Module Improts
# -----------------------------------------------------------------------------

from .plugins import Plugin, PluginProtocol

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class NetcadPlugin(Plugin):
    """
    Netcad design plugins support for CLI extensions, design features, etc.
    """

    _plugin_typeref = PluginProtocol
