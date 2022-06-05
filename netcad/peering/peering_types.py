#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Hashable

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, Field


__all__ = ["Peer", "PeeringEndpoint", "PeeringID"]

PeeringID = Hashable


class Peer(BaseModel):
    name: Hashable


class PeeringEndpoint(BaseModel):
    peer_id: PeeringID
    peer: Peer
    enabled: bool = Field(default=True)

    # assigned during the 'build' process
    endpoint_peer: Peer = Field(default=None)
