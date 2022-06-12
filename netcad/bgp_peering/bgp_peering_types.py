import dataclasses
from typing import Optional
from operator import attrgetter

from netcad.peering import Peer, PeeringID, PeeringEndpoint
from netcad.device import Device, to_interface_ip
from netcad.device import InterfaceIP

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["BGPSpeaker", "BGPSpeakerName", "BGPPeeringEndpoint"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

RouterID = InterfaceIP


@dataclasses.dataclass(frozen=True)
class BGPSpeakerName:
    hostname: str
    vrf: Optional[str] = None


class BGPPeeringEndpoint(PeeringEndpoint["BGPSpeaker", "BGPPeeringEndpoint"]):
    def __init__(
        self,
        via_ip: InterfaceIP,
        enabled: Optional[bool] = True,
        desc: Optional[str] = None,
    ):
        self.enabled = enabled
        self.via_ip = via_ip
        self._desc = desc

    @property
    def speaker(self) -> "BGPSpeaker":
        return self.peer

    @property
    def default_desc(self) -> str:
        rmt_end: BGPPeeringEndpoint = self.remote
        rmt_peer: BGPSpeaker = rmt_end.peer
        bgp_type = "iBGP" if self.peer.asn == rmt_peer.asn else "eBGP"
        name = rmt_peer.device.name
        return (
            f"{bgp_type} to {name} via {self.via_ip.interface.short_name} {self.via_ip}"
        )

    @property
    def desc(self) -> str:
        return self._desc or self.default_desc


class BGPSpeaker(Peer[Device, BGPPeeringEndpoint]):
    """
    BGPSpeaker represents an instance of a BGP router defined on a device. A
    device may have multiple BGP speakers for different VRFs.

    Attributes
    ----------
    device: Device
        The device instance hosting this speaker

    asn: int
        The BGP ASN value associated with this speaker

    router_id: RouterID
        The router ID associated with this speaker - typically the loopback IP
        address of the device/VRF.

    vrf: str, optional
        The name of the VRF the speaker is associated with.  The None value
        indicates the "default VRF", for whatever that means on the specific
        device.
    """

    def __init__(
        self, device: Device, asn: int, router_id: RouterID, vrf: Optional[str] = None
    ):
        # Use the tuple of the device name and VRF name as the peering-name.
        # This allows for a device/router to have multiple configurations based
        # n VRF.

        super().__init__(BGPSpeakerName(device.name, vrf))
        self.device = device
        self.asn = asn
        self.router_id = router_id
        self.vrf = vrf

    @property
    def neighbors(self) -> list[BGPPeeringEndpoint]:
        """
        Returns a sorted list of BGP neighbors defined for this speaker. The
        sort order is by the IP address.

        Returns
        -------
        List of endpoinds as described
        """
        return sorted(self.endpoints, key=attrgetter("via_ip"))

    def add_neighbor(self, peer_id: PeeringID, via: str):
        """
        Adds a new BGP neighbor endpoint to this speaker.

        Parameters
        ----------
        peer_id: PeeringID
            Uniquely identifies the BGP peering session so that the interface
            IP peering connections can be established.

        via: str
            The interface name that is hosting the BGP session connect. The
            interface profile must be an InterfaceL3 instance.

        Returns
        -------
        self instance for method chaing
        """
        with self.device.interfaces[via] as iface:
            try:
                ip = iface.profile.if_ipaddr.ip
            except (AttributeError, TypeError):
                raise RuntimeError(
                    f"{self.device.name}: Unable to add BGP neighbor via {via}, "
                    f"check interface profile for IP assignment"
                )

        ip = to_interface_ip(ip=ip, interface=iface)
        self.add_endpoint(peer_id=peer_id, endpoint=BGPPeeringEndpoint(via_ip=ip))
        return self

    def __repr__(self):
        attribs = repr(
            {"device": self.device.name, "asn": self.asn, "router_id": self.router_id}
        )
        return f"{self.__class__.__name__}({attribs})"
