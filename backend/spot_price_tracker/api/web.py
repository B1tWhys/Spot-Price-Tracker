from typing import List, Optional

from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session

from spot_price_tracker.api.responses import SpotInstancePriceResponse
from spot_price_tracker.db.db import get_db
from spot_price_tracker.db.models import CurrentSpotInstancePrice

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
    product_descriptions: Optional[List[str]] = Query(
        None,
        description="Filter by product description, e.g., LINUX/UNIX, SUSE Linux, etc",
    ),
    db: Session = Depends(get_db),
):
    """
    Fetch the latest spot instance price for each instance type in each region.
    """

    query = db.query(CurrentSpotInstancePrice).order_by(
        CurrentSpotInstancePrice.femto_usd_per_v_core_cycle.asc()
    )
    # Apply filters based on query parameters
    if instance_types:
        query = query.filter(CurrentSpotInstancePrice.instance_type.in_(instance_types))
    if regions:
        query = query.filter(CurrentSpotInstancePrice.region.in_(regions))
    if product_descriptions:
        query = query.filter(
            CurrentSpotInstancePrice.product_description.in_(product_descriptions)
        )

    query = query.limit(100)
    print(f"query = {str(query)}")
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
            femto_usd_per_v_core_cycle=round(price.femto_usd_per_v_core_cycle, 4),
            femto_usd_per_p_core_cycle=round(price.femto_usd_per_p_core_cycle, 4),
        )
        for price in prices
    ]
