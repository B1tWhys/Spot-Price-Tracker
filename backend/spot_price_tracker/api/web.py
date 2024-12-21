import fnmatch
from typing import List, Optional

from fastapi import FastAPI, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

from spot_price_tracker.api.requests import CurrentPricesQuery, CurrentPricesOrderBy
from spot_price_tracker.api.responses import SpotInstancePriceResponse, FilterOptions
from spot_price_tracker.db.db import get_db, get_instance_type_names
from spot_price_tracker.db.models import CurrentSpotInstancePrice, InstanceType

# Create FastAPI app
api = FastAPI(
    title="Spot Price Tracker",
    description="API for querying AWS spot instance prices.",
    version="1.0.0",
)

origins = [
    "*",
]
api.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"]
)


@api.get("/current", response_model=List[SpotInstancePriceResponse])
def get_current_prices(
    instance_types: Optional[List[str]] = Query(
        None,
        description="Filter by instance types, e.g., m5.large,m5.xlarge",
        alias="it",
    ),
    regions: Optional[List[str]] = Query(
        None, description="Filter by regions, e.g., us-east-1,us-west-2", alias="r"
    ),
    product_descriptions: Optional[List[str]] = Query(
        None,
        description="Filter by operating system, e.g., LINUX/UNIX, SUSE Linux, etc",
        alias="os",
    ),
    order_by: Optional[
        CurrentPricesOrderBy
    ] = CurrentPricesOrderBy.FEMTO_USD_PER_P_CORE_CYCLE,
    ascending: Optional[bool] = True,
    db: Session = Depends(get_db),
):
    """
    Fetch the latest spot instance price per instance type, availability zone and product description
    """

    return _get_current_prices_helper(
        db, instance_types, product_descriptions, regions, order_by, ascending
    )


@api.post("/current", response_model=List[SpotInstancePriceResponse])
def get_current_prices_post(
    query: Optional[CurrentPricesQuery] = None, db: Session = Depends(get_db)
):
    """
    Same as the GET version of this endpoint, but the filters are accepted in the request body to allow for very long
    lists of instance types & whatnot
    """
    args = dict(db=db)

    if query:
        if query.instance_types is not None:
            args["instance_types"] = query.instance_types
        if query.regions is not None:
            args["regions"] = query.regions
        if query.operating_systems is not None:
            args["product_descriptions"] = query.operating_systems
        if query.ascending is not None:
            args["asc"] = query.ascending
    print(f"{args=}")
    return _get_current_prices_helper(**args)


def _get_current_prices_helper(
    db,
    instance_types=None,
    product_descriptions=None,
    regions=None,
    order_by=None,
    asc=False,
):
    query = db.query(CurrentSpotInstancePrice)  # .order_by(
    #     CurrentSpotInstancePrice.femto_usd_per_v_core_cycle.asc()
    # )
    # Apply filters based on query parameters
    if instance_types is not None:
        if not instance_types:
            return []
        all_known_instance_types = get_instance_type_names(db)
        matched_instance_types = list(
            filter(
                lambda it: any(fnmatch.fnmatch(it, pat) for pat in instance_types),
                all_known_instance_types,
            )
        )
        print("filtering on instance types")
        query = query.filter(
            CurrentSpotInstancePrice.instance_type.in_(matched_instance_types)
        )
    if regions is not None:
        if not regions:
            return []
        query = query.filter(CurrentSpotInstancePrice.region.in_(regions))
    if product_descriptions is not None:
        if not product_descriptions:
            return []
        print("filtering on product description")
        query = query.filter(
            CurrentSpotInstancePrice.product_description.in_(product_descriptions)
        )
    order_col = CurrentSpotInstancePrice.femto_usd_per_v_core_cycle
    query = query.where(order_col.is_not(None))

    if order_by is not None:
        try:
            order_col = getattr(CurrentSpotInstancePrice, order_by.value)
        except AttributeError:
            pass

    query = query.order_by(order_col.asc() if asc else order_col.desc())
    query = query.limit(100)

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


@api.get("/filterOptions", response_model=FilterOptions)
def get_filter_options(db: Session = Depends(get_db)):
    instance_types = sorted(
        db.execute(select(InstanceType.instance_type.distinct()).order_by()).scalars()
    )
    operating_systems = sorted(
        db.execute(
            select(CurrentSpotInstancePrice.product_description.distinct())
        ).scalars()
    )
    regions = sorted(
        db.execute(select(CurrentSpotInstancePrice.region.distinct())).scalars()
    )

    return FilterOptions(
        instance_types=instance_types,
        operating_systems=operating_systems,
        regions=regions,
    )
