from netcad.peering import Peer, PeeringID, PeeringEndpoint
from netcad.device import Device, to_interface_ip
from netcad.device import InterfaceIP

RouterID = InterfaceIP


class BGPPeeringEndpoint(PeeringEndpoint):
    via_ip: InterfaceIP


class BGPSpeaker(Peer):
    def __init__(self, device: Device, asn: int, router_id: RouterID):
        super().__init__(name=(asn, router_id))
        self.device = device
        self.asn = asn
        self.router_id = router_id
        self.peering_endpoints = set()

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
            except (AttributeError, TypeError) as exc:
                raise RuntimeError(
                    f"Unable to add BGP neighbor via {via}, "
                    f"check interface profile: {str(exc)}"
                )

            ip = to_interface_ip(ip=ip, interface=iface)
            self.peering_endpoints.add(
                BGPPeeringEndpoint(peer=self, peer_id=peer_id, via_ip=ip)
            )

        return self

    def __repr__(self):
        attribs = repr(
            {"device": self.device.name, "asn": self.asn, "router_id": self.router_id}
        )
        return f"{self.__class__.__name__}({attribs})"
