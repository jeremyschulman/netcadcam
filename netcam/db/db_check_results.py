#  Copyright (c) 2025 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Iterator

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from sqlalchemy.dialects.postgresql import insert

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device

from .db_funcs import db_connect
from .db_tables import CheckResultTable


def db_check_results_save(
    device: Device, feature_name: str, collection: str, results: list[dict]
):
    db_name = device.design.name

    records = [
        dict(
            device=device.name,
            feature=feature_name,
            collection=collection,
            check_type=res["check"]["check_type"],
            check_id=res["check_id"],
            status=res["status"],
            result=res,
        )
        for res in results
    ]

    session = db_connect(db_name)

    stmt = insert(CheckResultTable).values(records)
    stmt = stmt.on_conflict_do_update(
        index_elements=["device", "feature", "check_type", "check_id", "status"],
        set_={"result": stmt.excluded.result},
        where=CheckResultTable.result != stmt.excluded.result,
    )

    session.execute(stmt)
    session.commit()


def db_check_results_get(
    session, device: str, feature: str, collection: str
) -> Iterator[dict]:
    records = session.query(CheckResultTable).filter(
        CheckResultTable.device == device,
        CheckResultTable.feature == feature,
        CheckResultTable.collection == collection,
    )

    return (rec.result for rec in records)
