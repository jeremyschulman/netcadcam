# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device.device_interface import DeviceInterface

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["PeerInterfaceId"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class PeerInterfaceId:
    """
    PeerInterfaceId is a descriptor that can be assigned to an
    InterfaceProfile.desc class attribute. It will return the peer interface
    "identity" that can be used, for example, as an interface description.  A
    network engineer may want to have a local interface description value set to
    be the identify of the remote interface.

    By default the DeviceInterface.device_ifname value is used.  The Caller can
    override this by selecting a different attribute designated in the
    PeerInterfaceId.__init__ method.
    """

    def __init__(self, if_attr: Optional[str] = "device_ifname"):
        self.if_attr = if_attr

    def __get__(self, instance, owner):
        # if no instance, then class lookup, return descriptor
        if instance is None:
            return self

        if_active: DeviceInterface = instance.interface
        if not (if_peer := if_active.cable_peer):
            raise RuntimeError(
                f"Unexpected missing interface peer on: {if_active.device_ifname}"
            )

        if not (if_peer_attr := getattr(if_peer, self.if_attr, None)):
            raise RuntimeError(
                f"Missing interface attribute {self.if_attr} on peer: {if_peer.device_ifname}"
            )

        return if_peer_attr
