#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad import __version__ as plugin_version  # noqa

# -----------------------------------------------------------------------------
# Private Module Imports
# -----------------------------------------------------------------------------

from .topology_feature import TopologyDesignFeature, TopologyFeatureLike

# sential object to mark an interface.cable_port_id  as do-not-check
from .checks.check_cabling_nei import NoValidateCabling
from .xcvr_matching import transceiver_model_matches, transceiver_type_matches

from . import cli


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def plugin_init(config: dict):
    """unused by init autoloading for builtin-plugin modules"""
    pass
