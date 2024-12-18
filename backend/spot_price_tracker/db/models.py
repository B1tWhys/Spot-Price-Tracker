from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    Text,
    Numeric,
    Computed,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class InstanceType(Base):
    __tablename__ = "instance_types"

    instance_type = Column(Text, primary_key=True)
    sustained_clock_speed_ghz = Column(Numeric(5, 3), nullable=True)
    p_cores = Column(Integer, nullable=False)
    v_cores = Column(Integer, nullable=True)
    p_core_cycles_per_hour = Column(
        Numeric, Computed("p_cores * sustained_clock_speed_ghz * (NUMERIC 3.6E12)")
    )
    v_core_cycles_per_hour = Column(
        Numeric, Computed("v_cores * sustained_clock_speed_ghz * (NUMERIC 3.6E12)")
    )


class CurrentSpotInstancePrice(Base):
    __tablename__ = "current_spot_instance_prices"

    instance_type = Column(
        Text,
        ForeignKey("instance_types.instance_type"),
        nullable=False,
        primary_key=True,
    )
    product_description = Column(String, nullable=True, primary_key=True)
    availability_zone = Column(String, nullable=False, primary_key=True)
    region = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), index=True)
    price_usd_hourly = Column(Numeric(11, 8), nullable=False)
    femto_usd_per_v_core_cycle = Column(Numeric, index=True)
    femto_usd_per_p_core_cycle = Column(Numeric, index=True)

    instance_type_obj = relationship("InstanceType")


class HistoricalSpotInstancePrice(Base):
    __tablename__ = "historical_spot_instance_prices"
    __table_args__ = {"timescaledb_hypertable": {"time_column_name": "timestamp"}}

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), primary_key=True)
    instance_type = Column(
        Text, ForeignKey("instance_types.instance_type"), nullable=False, index=True
    )
    product_description = Column(String, nullable=True, index=True)
    region = Column(String, nullable=False, index=True)
    availability_zone = Column(String, nullable=False, index=True)
    price_usd_hourly = Column(Numeric(11, 8), nullable=False)
    femto_usd_per_v_core_cycle = Column(Numeric, index=True)
    femto_usd_per_p_core_cycle = Column(Numeric, index=True)

    instance_type_obj = relationship("InstanceType")
