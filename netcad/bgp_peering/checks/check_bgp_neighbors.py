#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional
from typing import TYPE_CHECKING
from ipaddress import ip_address

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, Field

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.checks import CheckCollection, Check
from netcad.checks.check_registry import register_collection
from netcad.logger import get_logger

from ..bgp_nei_state import BgpNeighborState

if TYPE_CHECKING:
    from ..bgp_peering_design_service import BgpPeeringDesignService

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["BgpNeighborsCheckCollection", "BgpRouterCheck", "BgpNeighborCheck"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Check Device for router-ID, ASN
# -----------------------------------------------------------------------------


class BgpRouterCheckParams(BaseModel):
    name: str = Field(..., description="The device hostname")
    vrf: Optional[str] = Field(None, description="VRF used if not default")


class BgpRouterCheckExpectations(BaseModel):
    asn: int = Field(..., description="The device ASN value")
    router_id: str = Field(..., description="The device router-ID value")


class BgpRouterCheck(Check):
    check_type = "bgp-router"
    check_params: BgpRouterCheckParams
    expected_results: BgpRouterCheckExpectations

    def check_id(self) -> str:
        cp = self.check_params
        return cp.name if not cp.vrf else f"{cp.name}:{cp.vrf}"


# -----------------------------------------------------------------------------
# Check for a single BGP neighbor
# -----------------------------------------------------------------------------


class BgpNeighborCheckParams(BaseModel):
    nei_name: str = Field(..., description="The BGP speaker (device) name")
    nei_ip: str = Field(..., description="The BGP neighbor IP address")
    vrf: Optional[str] = Field(None, description="VRF used if not default")


class BgpNeighborCheckExpectations(BaseModel):
    remote_asn: int = Field(..., description="The remote BGP speaker ASN")
    state: BgpNeighborState = Field(
        ..., description="The BGP neighbor state, enum(int)"
    )


class BgpNeighborCheck(Check):
    check_type = "bgp-neighbor"
    check_params: BgpNeighborCheckParams
    expected_results: BgpNeighborCheckExpectations

    def check_id(self) -> str:
        return str(self.check_params.nei_ip)


# -----------------------------------------------------------------------------
# Check for exclusive list of BGP Neighbors
# -----------------------------------------------------------------------------


class BgpNeighborExclusiveListCheck(Check):
    check_type = "exclusive_list"
    expected_results: List[BgpNeighborCheckExpectations]

    def check_id(self) -> str:
        return self.check_type


# -----------------------------------------------------------------------------
#
#
# -----------------------------------------------------------------------------


class BgpNeighborCollectionChecks(BaseModel):
    routers: List[BgpRouterCheck]
    neighbors: List[BgpNeighborCheck]

    def __len__(self):
        """define length for composite checks class"""
        return len(self.neighbors) + 1


@register_collection
class BgpNeighborsCheckCollection(CheckCollection):
    name = "bgp-peering"
    checks: BgpNeighborCollectionChecks

    @classmethod
    def build(
        cls, device: Device, design_service: "BgpPeeringDesignService"
    ) -> "BgpNeighborsCheckCollection":

        # import here to avoid circular imports
        from ..bgp_peering_design_service import BgpPeeringDesignService

        services: List[BgpPeeringDesignService] = device.services_of(
            BgpPeeringDesignService
        )

        nei_checks = list()
        rtr_checks = list()

        # find matching to device hostname

        routers = [
            spkr
            for bgp_svc in services
            for spkr_name, spkr in bgp_svc.speakers.items()
            if spkr_name.hostname == device.name
        ]

        if not routers:
            get_logger().error(f"Device {device.name} does not have any BGP routers")
            raise RuntimeError()

        for bgp_spkr in routers:

            rtr_checks.append(
                BgpRouterCheck(
                    check_params=BgpRouterCheckParams(
                        name=device.name, vrf=bgp_spkr.vrf
                    ),
                    expected_results=BgpRouterCheckExpectations(
                        asn=bgp_spkr.asn, router_id=str(bgp_spkr.router_id)
                    ),
                )
            )

            for bgp_nei_rec in bgp_spkr.neighbors:
                remote = bgp_nei_rec.remote
                nei_checks.append(
                    BgpNeighborCheck(
                        check_params=BgpNeighborCheckParams(
                            nei_name=remote.speaker.device.name,
                            nei_ip=str(remote.via_ip),
                            vrf=bgp_spkr.vrf,
                        ),
                        expected_results=BgpNeighborCheckExpectations(
                            remote_asn=remote.speaker.asn,
                            state=BgpNeighborState.ESTABLISHED,
                        ),
                    )
                )

        collection = BgpNeighborsCheckCollection(
            device=device.name,
            exclusive=True,
            checks=BgpNeighborCollectionChecks(
                routers=rtr_checks,
                neighbors=nei_checks,
            ),
        )

        # return the test-cases sorted by Neighbor IP address
        collection.checks.neighbors.sort(
            key=lambda c: ip_address(c.check_params.nei_ip)
        )
        return collection
