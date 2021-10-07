# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .client import NetboxClient

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["NetboxCabling"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class NetboxCabling(NetboxClient):
    async def cable_interfaces(self, if_id_a: int, if_id_b: int) -> dict:
        res = await self.post(
            self.API_CABLES,
            json={
                "status": "connected",
                "termination_a_type": "dcim.interface",
                "termination_a_id": if_id_a,
                "termination_b_type": "dcim.interface",
                "termination_b_id": if_id_b,
            },
        )
        if res.is_error:
            raise RuntimeError(
                f"cable failured between {if_id_a}:{if_id_b} - {res.text}"
            )

        return res.json()
