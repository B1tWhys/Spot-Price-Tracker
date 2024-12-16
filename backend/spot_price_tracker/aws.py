from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

import boto3
import typer

from spot_price_tracker.db.models import SpotInstancePrice, InstanceType


@dataclass
class RegionalSpotPriceHistoryQuery:
    region_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    instance_types: Optional[List[str]] = None


def get_aws_regions() -> List[str]:
    """
    Fetch the list of available AWS regions

    :rtype: List[str]
    """
    try:
        ec2_client = boto3.client("ec2")
        response = ec2_client.describe_regions(
            AllRegions=False
        )  # Only return regions that are enabled for my account
        regions = [region["RegionName"] for region in response["Regions"]]
        return regions
    except Exception as e:
        raise RuntimeError(f"Failed to fetch AWS regions: {e}")


def _get_regional_spot_price_history(
    query: RegionalSpotPriceHistoryQuery,
) -> List[SpotInstancePrice]:
    """
    Fetch the spot price history for a single region based on the provided query object.

    :param query: An instance of RegionalSpotPriceHistoryQuery containing the query parameters.
    :return: A list of SpotInstancePrice objects for the specified region.
    """
    typer.echo(f"Fetching spot price history: {query}")
    # boto3.set_stream_logger('', logging.DEBUG)
    ec2_client = boto3.client("ec2", region_name=query.region_name)

    start_time = query.start_time.astimezone(timezone.utc)
    end_time = query.end_time.astimezone(timezone.utc) or datetime.now(timezone.utc)
    params = {"StartTime": start_time, "EndTime": end_time, "NextToken": ""}
    if query.instance_types:
        params["InstanceTypes"] = query.instance_types

    spot_price_history = []
    while True:
        response = ec2_client.describe_spot_price_history(**params)
        spot_price_history.extend(response["SpotPriceHistory"])
        if "NextToken" in response and response["NextToken"]:
            params["NextToken"] = response["NextToken"]
        else:
            break

    spot_prices = [
        SpotInstancePrice(
            instance_type=record["InstanceType"],
            product_description=record.get("ProductDescription", None),
            price_usd_hourly=float(record["SpotPrice"]),
            region=query.region_name,
            availability_zone=record["AvailabilityZone"],
            timestamp=(
                record["Timestamp"]
                if isinstance(record["Timestamp"], datetime)
                else datetime.fromisoformat(record["Timestamp"])
            ),
        )
        for record in spot_price_history
    ]
    spot_prices = list(
        filter(lambda sp: start_time <= sp.timestamp <= end_time, spot_prices)
    )
    return spot_prices


def get_spot_price_history(
    queries: List[RegionalSpotPriceHistoryQuery],
    max_threads: int = 5,
) -> List[SpotInstancePrice]:
    """
    Fetch spot price history for multiple regions.

    :param queries: A list of RegionalSpotPriceHistoryQuery objects, each specifying the parameters for a region.
    :param max_threads: The maximum number of threads to use for concurrent requests.

    :return: A flattened list of `SpotInstancePrice` objects for all regions.
    """

    with ThreadPoolExecutor(max_threads) as executor:
        futures = {
            executor.submit(_get_regional_spot_price_history, query): query.region_name
            for query in queries
        }

        # Collect results as tasks complete
        spot_prices = []
        for future in as_completed(futures):
            region = futures[future]
            try:
                region_spot_prices = future.result()
                spot_prices.extend(region_spot_prices)
            except Exception as e:
                raise RuntimeError(
                    f"Error fetching spot price history for region {region}: {e}", e
                )

    return spot_prices


def _safe_get_clock_speed(instance_type_data):
    return instance_type_data.get("ProcessorInfo", {}).get(
        "SustainedClockSpeedInGhz", None
    )


def get_instance_types() -> List[InstanceType]:
    """
    Fetch details about EC2 instance types from AWS

    :return: A list of `InstanceType` objects that can be stored in the database.
    :raises RuntimeError: If there is an error fetching instance types from AWS.
    """
    try:
        ec2_client = boto3.client("ec2")
        typer.echo("Fetching instance types")

        instance_types = []
        paginator = ec2_client.get_paginator("describe_instance_types")
        for page in paginator.paginate():
            for instance_type_data in page["InstanceTypes"]:
                try:
                    instance_types.append(
                        InstanceType(
                            instance_type=instance_type_data["InstanceType"],
                            v_cores=instance_type_data["VCpuInfo"]["DefaultVCpus"],
                            cores=instance_type_data["VCpuInfo"].get(
                                "DefaultCores",
                                instance_type_data["VCpuInfo"]["DefaultVCpus"] // 2,
                            ),
                            sustained_clock_speed_ghz=_safe_get_clock_speed(
                                instance_type_data
                            ),
                        )
                    )
                except KeyError as e:
                    raise KeyError(
                        f"Failed to parse instance type data. Missing key in: {instance_type_data}",
                        e,
                    )
        return instance_types
    except Exception as e:
        raise RuntimeError(f"Failed to fetch instance types: {e}", e)
