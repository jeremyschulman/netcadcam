#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from netcad import __version__ as plugin_version  # noqa

from .client import NetboxClient
from .netbox_origin import NetboxOrigin as Origin
from .netbox_origin_devicetype import NetboxOriginDeviceType


def plugin_init(config: dict):
    """unused by init autoloading for builtin-plugin modules"""
    pass
