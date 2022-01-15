#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from .vlan_profile import VlanProfile, VlanProfileLike
from .descriptor_peer_vlan_info import VlansFromPeer
from .descriptor_vlan_all import VlansAll
from .profiles.l2_interfaces import InterfaceL2, InterfaceL2Access, InterfaceL2Trunk
from .profiles.vlan_interface import InterfaceVlan
from . import cli

from netcad import __version__ as plugin_version  # noqa


def plugin_init(config: dict):

    pass
