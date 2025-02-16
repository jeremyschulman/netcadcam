#  Copyright (c) 2025 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


from sqlalchemy import Column, Integer, String, UniqueConstraint, Index, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSONB

TableBase = declarative_base()


class DeviceTable(TableBase):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    alias = Column(String, nullable=False)
    os = Column(String, nullable=False)
    device_type = Column(String, nullable=False)

    __table_args__ = (UniqueConstraint("name", name="uq_device_name"),)

    interfaces = relationship("InterfacesTable", back_populates="device")


class InterfacesTable(TableBase):
    __tablename__ = "interfaces"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    desc = Column(String, nullable=False)
    profile = Column(String, nullable=False)

    # Foreign key linking this interface to a device
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    # Set up back reference to the DeviceTable
    device = relationship("DeviceTable", back_populates="interfaces")

    __table_args__ = (
        UniqueConstraint(
            "device_id", "name", name="uq_device_ifname"
        ),  # This enforces the uniqueness
    )


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
