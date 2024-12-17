from typing import List, Optional

from fastapi import FastAPI, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from spot_price_tracker.api.responses import SpotInstancePriceResponse
from spot_price_tracker.db.db import get_db
from spot_price_tracker.db.models import SpotInstancePrice

# Create FastAPI app
api = FastAPI(
    title="Spot Price Tracker",
    description="API for querying AWS spot instance prices.",
    version="1.0.0",
)


@api.get("/current", response_model=List[SpotInstancePriceResponse])
def get_current_prices(
    instance_types: Optional[List[str]] = Query(
        None, description="Filter by instance types, e.g., m5.large,m5.xlarge"
    ),
    regions: Optional[List[str]] = Query(
        None, description="Filter by regions, e.g., us-east-1,us-west-2"
    ),
    db: Session = Depends(get_db),
):
    """
    Fetch the latest spot instance price for each instance type in each region.
    """
    # Subquery: Get the latest timestamp for each instance type and region
    subquery = (
        db.query(
            SpotInstancePrice.instance_type,
            SpotInstancePrice.region,
            func.max(SpotInstancePrice.timestamp).label("latest_timestamp"),
        )
        .group_by(SpotInstancePrice.instance_type, SpotInstancePrice.region)
        .subquery()
    )

    # Join the main table with the subquery to get the full row details
    query = db.query(SpotInstancePrice).join(
        subquery,
        (
            (SpotInstancePrice.instance_type == subquery.c.instance_type)
            & (SpotInstancePrice.region == subquery.c.region)
            & (SpotInstancePrice.timestamp == subquery.c.latest_timestamp)
        ),
    )

    # Apply filters based on query parameters
    if instance_types:
        query = query.filter(SpotInstancePrice.instance_type.in_(instance_types))
    if regions:
        query = query.filter(SpotInstancePrice.region.in_(regions))

    # Execute query
    prices = query.all()

    # Transform results into Pydantic models
    return [
        SpotInstancePriceResponse(
            instance_type=price.instance_type,
            product_description=price.product_description,
            price_usd_hourly=price.price_usd_hourly,
            region=price.region,
            availability_zone=price.availability_zone,
            timestamp=price.timestamp.isoformat(),
            v_cores=price.instance_type_obj.v_cores,
            cores=price.instance_type_obj.p_cores,
            sustained_clock_speed_ghz=price.instance_type_obj.sustained_clock_speed_ghz,
        )
        for price in prices
    ]
