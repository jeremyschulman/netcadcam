#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from .. import plugin_version  # noqa required for plugin-framework
from .pull import plugin_origin_pull
from .push import plugin_origin_push

plugin_init = lambda config: True
