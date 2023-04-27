import dataclasses
from typing import Optional
from operator import attrgetter

from netcad.peering import Peer, PeeringEndpoint
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
    EBGP_TOKEN = "eBGP"
    IBGP_TOKEN = "iBGP"

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
    def bgp_type(self) -> str:
        rmt_peer = self.remote.peer
        return self.IBGP_TOKEN if self.peer.asn == rmt_peer.asn else self.EBGP_TOKEN

    @property
    def default_desc(self) -> str:
        rmt_peer = self.remote.peer
        name = rmt_peer.device.name
        return f"{self.bgp_type} to {name} via {self.via_ip.interface.short_name} {self.via_ip}"

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

    router_id: RouterID, optional
        The router ID associated with this speaker - typically the loopback IP
        address of the device/VRF.  If not provided, this value defaults to the
        device.primary_ip.

    vrf: str, optional
        The name of the VRF the speaker is associated with.  The None value
        indicates the "default VRF", for whatever that means on the specific
        device.

    rd: str, optional
        The route distinguisher to be appended to all VPN prefixes creating
        unique prefixes. This requires multiprotocol BGP: MP-BGP.

    rt: str, optional
        The route target (extended community attribute) is attached to to the route
        and tells the receiving router what VRF to put the route into.
    """

    def __init__(
        self,
        device: Device,
        asn: int,
        router_id: Optional[RouterID] = None,
        vrf: Optional[str] = None,
        rd: Optional[str] = None,
        rt: Optional[str] = None,
    ):
        # Use the tuple of the device name and VRF name as the peering-name.
        # This allows for a device/router to have multiple configurations based
        # n VRF.

        super().__init__(BGPSpeakerName(device.name, vrf))
        self.device = device
        self.asn = asn
        self.router_id = router_id or device.primary_ip
        self.vrf = vrf
        self.rd = rd
        self.rt = rt

    @property
    def speaker_id(self) -> str:
        return f'{self.device.name}:{self.router_id}:{self.vrf or "default"}'

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

    def make_peer_id(self, other: "BGPSpeaker") -> str:
        return "+".join(sorted((self.speaker_id, other.speaker_id)))

    def add_neighbor(self, bgp_nei: "BGPSpeaker", via: str):
        """
        Adds a new BGP neighbor endpoint to this speaker.

        Parameters
        ----------
        # peer_id: PeeringID
        #     Uniquely identifies the BGP peering session so that the interface
        #     IP peering connections can be established.

        bgp_nei: BGPSpeaker
            The other BGP speaker for which this neighbor relationship is
            formed.

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

        self.add_endpoint(
            peer_id=self.make_peer_id(bgp_nei), endpoint=BGPPeeringEndpoint(via_ip=ip)
        )

        return self

    def __repr__(self):
        attribs = repr(
            {
                "device": self.device.name,
                "asn": self.asn,
                "router_id": self.router_id,
                "vrf": self.vrf,
                "rd": self.rd,
                "rt": self.rt,
            }
        )
        return f"{self.__class__.__name__}({attribs})"
