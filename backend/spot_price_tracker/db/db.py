import os
from datetime import datetime, timezone
from typing import Dict, Set

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session

from spot_price_tracker.db.models import SpotInstancePrice, InstanceType

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise EnvironmentError(
        "The DATABASE_URL environment variable is not set. "
        "Please set it to a valid database connection string. "
        "For local development, you can use 'sqlite:///example.db'."
    )

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency to get a new database session for each use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_database():
    """
    Seed the database with test data for local development.
    """
    db: Session = next(get_db())

    instance_types = [
        InstanceType(
            instance_type="m5.large", v_cores=2, cores=1, sustained_clock_speed_ghz=2.3
        ),
        InstanceType(
            instance_type="m5.xlarge", v_cores=4, cores=2, sustained_clock_speed_ghz=2.5
        ),
    ]
    db.add_all(instance_types)

    # Add spot instance prices
    spot_prices = [
        SpotInstancePrice(
            instance_type="m5.large",
            product_description="Linux/UNIX",
            price_usd_hourly=0.034,
            region="us-east-1",
            availability_zone="us-east-1a",
            timestamp=datetime(2024, 12, 14, 10, 0, 0, tzinfo=timezone.utc),
        ),
        SpotInstancePrice(
            instance_type="m5.large",
            product_description="Windows",
            price_usd_hourly=0.033,
            region="us-east-1",
            availability_zone="us-east-1a",
            timestamp=datetime(2024, 12, 14, 9, 0, 0, tzinfo=timezone.utc),
        ),
        SpotInstancePrice(
            instance_type="m5.xlarge",
            product_description="SUSE Linux",
            price_usd_hourly=0.068,
            region="us-east-1",
            availability_zone="us-east-1b",
            timestamp=datetime(2024, 12, 14, 11, 0, 0, tzinfo=timezone.utc),
        ),
        SpotInstancePrice(
            instance_type="m5.xlarge",
            product_description="Linux/UNIX",
            price_usd_hourly=0.067,
            region="us-west-1",
            availability_zone="us-west-1a",
            timestamp=datetime(2024, 12, 14, 11, 0, 0, tzinfo=timezone.utc),
        ),
    ]
    db.add_all(spot_prices)

    db.commit()


def get_latest_timestamps_by_region(db: Session) -> Dict[str, datetime]:
    """
    Fetch the latest timestamp for each region from the SpotInstancePrice table.

    :param db: SQLAlchemy database session.
    :return: A dictionary mapping region names to timestamps representing the latest value we have for that region.
    """
    results = (
        db.query(
            SpotInstancePrice.region,
            func.max(SpotInstancePrice.timestamp).label("latest_timestamp"),
        )
        .group_by(SpotInstancePrice.region)
        .all()
    )

    return {region: latest_timestamp for region, latest_timestamp in results}


def get_instance_type_names(db: Session) -> Set[str]:
    """
    Fetch a list of all instance type names from the `instance_types` table.

    :param db: SQLAlchemy database session.
    :return: A set of instance type names (e.g., ["m5.large", "m5.xlarge"]).
    """
    return {row.instance_type for row in db.query(InstanceType.instance_type).all()}
