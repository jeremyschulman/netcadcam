#  Copyright (c) 2025 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import TYPE_CHECKING

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import igraph
from sqlalchemy.orm.session import Session
from sqlalchemy.dialects.postgresql import insert

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

if TYPE_CHECKING:
    from netcad.services import DesignServiceCheck, DesignService

from .db_tables import ServiceCheckResultTable

# -----------------------------------------------------------------------------
#
#                               CODE BEGISN
#
# -----------------------------------------------------------------------------


def db_service_check_save(
    db: Session,
    service: "DesignService",
    check: "DesignServiceCheck",
    node: igraph.Vertex,
):
    result = check.model_dump()

    stmt = insert(ServiceCheckResultTable).values(
        node_id=node.index,
        service=service.name,
        ok=check.ok,
        check_type=check.check_type,
        check_id=check.check_id,
        result=result,
    )

    stmt = stmt.on_conflict_do_update(
        index_elements=["service", "check_type", "check_id"],
        set_={"result": result, "node_id": node.index},
    )

    db.execute(stmt)
    db.commit()
