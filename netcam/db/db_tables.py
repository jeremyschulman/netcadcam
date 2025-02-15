from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import JSONB

TableBase = declarative_base()


class CheckResultTable(TableBase):
    __tablename__ = "check_results"

    id = Column(Integer, primary_key=True)
    feature = Column(String, nullable=False)
    device = Column(String, nullable=False)
    check_type = Column(String, nullable=False)
    check_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    result = Column(JSONB)

    __table_args__ = (
        UniqueConstraint(
            "device",
            "feature",
            "check_type",
            "check_id",
            "status",
            name="uix_device_feature_check",
        ),
    )
