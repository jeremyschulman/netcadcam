#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from netcad import __version__ as plugin_version  # noqa
from .client import NetboxClient
from .netbox_devicetype import NetboxOriginDeviceType as DeviceType


def plugin_init(config: dict):  # noqa
    """unused by init autoloading for builtin-plugin modules"""
    pass


def plugin_origin_item(cache_item_type: str, origin):
    if cache_item_type == "DeviceType":
        return DeviceType(origin_spec=origin)
