#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Dict, Optional

from .. import plugin_version  # noqa required for plugin-framework

from .pull import plugin_origin_pull
from .push import plugin_origin_push
from . import plugin_config


def plugin_init(config: dict):
    plugin_config.g_netbox_topology_config.update(config)
