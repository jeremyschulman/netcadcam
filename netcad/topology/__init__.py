#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from .topology_design_service import TopologyDesignService, TopologyServiceLike

# sential object to mark an interface.cable_port_id  as do-not-check
from .check_cabling_nei import NoValidateCabling
