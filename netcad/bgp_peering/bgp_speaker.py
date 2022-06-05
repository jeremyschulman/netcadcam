from ipaddress import IPv4Address, IPv6Interface

from netcad.peering import Peer
from netcad.device import Device


RouterID = IPv4Address | IPv6Interface


class BGPSpeaker(Peer):
    def __init__(self, device: Device, asn: int, router_id: RouterID):
        super().__init__(name=(asn, router_id))
        self.device = device
        self.asn = asn
        self.router_id = router_id

    def __repr__(self):
        attribs = repr(
            {"device": self.device.name, "asn": self.asn, "router_id": self.router_id}
        )
        return f"{self.__class__.__name__}({attribs})"
