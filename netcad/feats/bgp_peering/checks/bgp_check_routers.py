#  Copyright (c) 20222 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional, ClassVar

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, Field

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.checks import CheckCollection, Check, CheckResult, CheckMeasurement
from netcad.logger import get_logger

from ..bgp_peering_design_feature import BgpPeeringDesignFeature

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["BgpRoutersCheckCollection", "BgpRouterCheck", "BgpRouterCheckResult"]


# -----------------------------------------------------------------------------
# Check Device for router-ID, ASN
# -----------------------------------------------------------------------------


class BgpRouterCheckParams(BaseModel):
    name: str = Field(..., description="The device hostname")
    vrf: Optional[str] = Field(None, description="VRF used if not default")


class BgpRouterCheck(Check):
    """
    Validate that the device has a BGP speaker operating, i.e. configured for
    running BGP and showing that it is operationally present.
    """

    check_type: str = "bgp-router"

    Params = BgpRouterCheckParams

    class Expect(BaseModel):
        asn: int = Field(..., description="The speaker ASN value")
        router_id: str = Field(..., description="The speaker router-ID value (IP addr)")

    check_params: BgpRouterCheckParams
    expected_results: Expect

    def check_id(self) -> str:
        """
        The check ID value is the device hostname, and optionally the VRF name
        if this BGP speaker is using a VRF.
        """
        cp = self.check_params
        return cp.name if not cp.vrf else f"{cp.name}:{cp.vrf}"


class BgpRouterCheckResult(CheckResult[BgpRouterCheck]):
    class Measurement(BgpRouterCheck.Expect, CheckMeasurement):
        pass

    measurement: Measurement = None


# -----------------------------------------------------------------------------
#
#
# -----------------------------------------------------------------------------


@BgpPeeringDesignFeature.register_check_collection
class BgpRoutersCheckCollection(CheckCollection):
    name: ClassVar[str] = "bgp-routers"
    checks: List[BgpRouterCheck]

    @classmethod
    def build(
        cls, device: Device, design_feature: "BgpPeeringDesignFeature"
    ) -> "BgpRoutersCheckCollection":
        # import here to avoid circular imports
        from ..bgp_peering_design_feature import BgpPeeringDesignFeature

        services: List[BgpPeeringDesignFeature] = device.services_of(
            BgpPeeringDesignFeature
        )

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
                    check_params=BgpRouterCheck.Params(
                        name=device.name, vrf=bgp_spkr.vrf
                    ),
                    expected_results=BgpRouterCheck.Expect(
                        asn=bgp_spkr.asn, router_id=str(bgp_spkr.router_id)
                    ),
                )
            )

        collection = BgpRoutersCheckCollection(
            device=device.name, exclusive=True, checks=rtr_checks
        )

        # return the test-cases sorted by check parameter values.
        collection.checks.sort(key=lambda c: tuple(c.check_params.dict().values()))
        return collection
