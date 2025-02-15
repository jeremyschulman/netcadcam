#  Copyright (c) 2025 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


from sqlalchemy import Column, Integer, String, UniqueConstraint, Index
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import JSONB

TableBase = declarative_base()


class CheckResultTable(TableBase):
    __tablename__ = "check_results"

    id = Column(Integer, primary_key=True)
    feature = Column(String, nullable=False)
    collection = Column(String, nullable=False)
    device = Column(String, nullable=False)
    check_type = Column(String, nullable=False)
    check_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    result = Column(JSONB)

    __table_args__ = (
        Index("device", "feature", "check_type", "check_id"),
        UniqueConstraint(
            "device",
            "feature",
            "check_type",
            "check_id",
            "status",
            name="uix_device_feature_check",
        ),
    )
