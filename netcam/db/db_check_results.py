from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert

from netcad.device import Device
from .db_funcs import db_connect
from .db_tables import CheckResultTable


def db_check_results_save(device: Device, feature_name: str, results: list[dict]):
    db_name = device.design.name

    records = [
        dict(
            feature=feature_name,
            device=device.name,
            check_type=res["check"]["check_type"],
            check_id=res["check_id"],
            status=res["status"],
            result=res,
        )
        for res in results
    ]

    session = sessionmaker(bind=db_connect(db_name))()

    stmt = insert(CheckResultTable).values(records)
    stmt = stmt.on_conflict_do_update(
        index_elements=["device", "feature", "check_type", "check_id", "status"],
        set_={"result": stmt.excluded.result},
        where=CheckResultTable.result != stmt.excluded.result,
    )

    session.execute(stmt)
    session.commit()
