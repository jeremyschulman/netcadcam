from typing import Optional
from operator import attrgetter

from netcad.peering import Peer, PeeringID, PeeringEndpoint
from netcad.device import Device, to_interface_ip
from netcad.device import InterfaceIP

RouterID = InterfaceIP


class BGPPeeringEndpoint(PeeringEndpoint["BGPSpeaker", "BGPPeeringEndpoint"]):
    desc: str
    via_ip: InterfaceIP

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
    def speaker(self):
        return self.peer

    @property
    def default_desc(self):
        rmt_end: BGPPeeringEndpoint = self.remote
        rmt_peer: BGPSpeaker = rmt_end.peer
        bgp_type = "iBGP" if self.peer.asn == rmt_peer.asn else "eBGP"
        return f"{bgp_type} to {rmt_peer.name} via {self.via_ip.interface.short_name} {self.via_ip}"

    @property
    def desc(self):
        return self._desc or self.default_desc


class BGPSpeaker(Peer[Device, BGPPeeringEndpoint]):
    def __init__(self, device: Device, asn: int, router_id: RouterID):
        super().__init__(name=device.name)
        self.device = device
        self.asn = asn
        self.router_id = router_id

    @property
    def neighbors(self) -> list[BGPPeeringEndpoint]:
        return sorted(self.endpoints, key=attrgetter("via_ip"))

    def add_neighbor(self, peer_id: PeeringID, via: str):
        """

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
