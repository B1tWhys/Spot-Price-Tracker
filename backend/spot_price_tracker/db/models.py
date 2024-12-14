from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class InstanceType(Base):
    __tablename__ = 'instance_types'

    instance_type = Column(String, primary_key=True, index=True)
    v_cores = Column(Integer, nullable=False)
    sustained_clock_speed_ghz = Column(Float, nullable=False)

    # Relationship to SpotInstancePrice
    spot_prices = relationship("SpotInstancePrice", back_populates="instance_type_obj")

    def __repr__(self):
        return (
            f"<InstanceType(instance_type='{self.instance_type}', "
            f"v_cores={self.v_cores}, "
            f"sustained_clock_speed_ghz={self.sustained_clock_speed_ghz})>"
        )


class SpotInstancePrice(Base):
    __tablename__ = 'spot_instance_prices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    instance_type = Column(String, ForeignKey('instance_types.instance_type'), nullable=False, index=True)
    price_usd_hourly = Column(Float, nullable=False)
    region = Column(String, nullable=False, index=True)
    availability_zone = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)

    # Additional index on timestamp for efficient ordering
    __table_args__ = (Index('idx_timestamp', 'timestamp'),)

    # Relationship to InstanceType
    instance_type_obj = relationship("InstanceType", back_populates="spot_prices")

    def __repr__(self):
        return (
            f"<SpotInstancePrice(instance_type='{self.instance_type}', "
            f"price_usd_hourly={self.price_usd_hourly}, "
            f"region='{self.region}', "
            f"availability_zone='{self.availability_zone}', "
            f"timestamp='{self.timestamp}')>"
        )
