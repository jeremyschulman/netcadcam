from typing import Set, Optional

from netcad.peering import PeeringID

from .bgp_speaker import BGPSpeaker

BGPPeerID = PeeringID


class BGPNeighborSession:
    pass


class BGPPeerNeighbors:
    def __init__(self, peer_id: BGPPeerID, enabled: Optional[bool] = True):
        self.peer_id = peer_id
        self.enabled = enabled
        self.speakers: Set[BGPSpeaker] = set()

    def add_sesson(self, speaker: BGPSpeaker, session: BGPNeighborSession):
        ...

    def add_speakers(self, *speakers: BGPSpeaker):
        self.speakers.update(speakers)
        return self
