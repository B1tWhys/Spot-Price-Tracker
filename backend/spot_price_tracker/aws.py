from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from queue import Queue
from typing import List, Optional, Generator

import boto3
import numpy as np
import typer

from spot_price_tracker.db import db
from spot_price_tracker.db.models import HistoricalSpotInstancePrice, InstanceType

running = True


@dataclass
class RegionalSpotPriceHistoryQuery:
    region_name: str
    start_time: datetime
    end_time: Optional[datetime] = None


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
    query: RegionalSpotPriceHistoryQuery, output_queue: Queue
):
    """
    Fetch the spot price history for a single region based on the provided query object.

    :param query: An instance of RegionalSpotPriceHistoryQuery containing the query parameters.
    :return: A list of HistoricalSpotInstancePrice objects for the specified region.
    """
    typer.echo(f"Fetching spot price history: {query}")
    with next(db.get_db()) as db_session:
        instance_type_details = db.get_all_instance_types(db_session)
    ec2_client = boto3.client("ec2", region_name=query.region_name)

    start_time = query.start_time.astimezone(timezone.utc)
    end_time = query.end_time.astimezone(timezone.utc) or datetime.now(timezone.utc)
    params = {"StartTime": start_time, "EndTime": end_time, "NextToken": ""}

    try:
        while running:
            response = ec2_client.describe_spot_price_history(**params)
            typer.echo(f"Got page of results for region: {query.region_name}")
            for resp_record in response["SpotPriceHistory"]:
                if (
                    instance_type_name := resp_record["InstanceType"]
                ) not in instance_type_details:
                    continue
                timestamp = resp_record["Timestamp"]
                if not (start_time <= timestamp <= end_time):
                    continue
                instance_type = instance_type_details[instance_type_name]
                price_hourly = np.float64(resp_record["SpotPrice"])
                femto_price_per_p_cycle = (
                    float(
                        1e15
                        * price_hourly
                        / np.float64(instance_type.p_core_cycles_per_hour)
                    )
                    if instance_type.p_core_cycles_per_hour is not None
                    else None
                )
                femto_price_per_v_cycle = (
                    float(
                        1e15
                        * price_hourly
                        / np.float64(instance_type.v_core_cycles_per_hour)
                    )
                    if instance_type.v_core_cycles_per_hour is not None
                    else None
                )

                db_record = dict(
                    timestamp=timestamp,
                    instance_type=instance_type_name,
                    product_description=resp_record["ProductDescription"],
                    region=query.region_name,
                    availability_zone=resp_record["AvailabilityZone"],
                    price_usd_hourly=resp_record["SpotPrice"],
                    femto_usd_per_p_core_cycle=femto_price_per_p_cycle,
                    femto_usd_per_v_core_cycle=femto_price_per_v_cycle,
                )
                output_queue.put(db_record)

            if "NextToken" in response and response["NextToken"]:
                params["NextToken"] = response["NextToken"]
            else:
                break
    finally:
        output_queue.put(query.region_name)


def get_spot_price_history(
    queries: List[RegionalSpotPriceHistoryQuery],
    instance_type_details: dict[str, InstanceType],
    max_threads: int = 5,
) -> Generator[HistoricalSpotInstancePrice, None, None]:
    """
    Fetch spot price history for multiple regions.

    :param queries: A list of RegionalSpotPriceHistoryQuery objects, each specifying the parameters for a region.
    :param instance_type_details: Map of string to InstanceType records that should be fetched
    :param max_threads: The maximum number of threads to use for concurrent requests.

    :yields: HistoricalSpotInstancePrice records
    """
    q = Queue(maxsize=50)
    with ThreadPoolExecutor(max_threads) as executor:
        futures = {}
        try:
            for query in queries:
                future = executor.submit(_get_regional_spot_price_history, query, q)
                futures[query.region_name] = future

            while futures:
                record = q.get()
                if type(record) is str:
                    typer.echo(f"Region {record} done!")
                    try:
                        as_completed((futures[record],))
                        del futures[record]
                        continue
                    except Exception as e:
                        typer.echo(f"Failed to get spot prices for region {record}")
                        for future in futures.values():
                            future.cancel()
                        raise e

                # print(f"Yielding record: {record}")
                yield HistoricalSpotInstancePrice(**record)
            typer.echo("All spot history records have been retrieved")
        except KeyboardInterrupt as e:
            global running
            running = False
            print("Canceling futures")
            for future in futures.values():
                future.cancel()
            print("Purging queue")
            while not q.empty():
                q.get()
            raise e


def _safe_get_clock_speed(instance_type_data):
    return instance_type_data.get("ProcessorInfo", {}).get(
        "SustainedClockSpeedInGhz", None
    )


def get_instance_types(region) -> List[InstanceType]:
    """
    Fetch details about EC2 instance types from AWS

    :return: A list of `InstanceType` objects that can be stored in the database.
    :raises RuntimeError: If there is an error fetching instance types from AWS.
    """
    try:
        ec2_client = boto3.client("ec2", region_name=region)
        typer.echo(f"Fetching instance types from region: {region}")

        instance_types = []
        paginator = ec2_client.get_paginator("describe_instance_types")
        for page in paginator.paginate():
            for instance_type_data in page["InstanceTypes"]:
                try:
                    instance_types.append(
                        InstanceType(
                            instance_type=instance_type_data["InstanceType"],
                            sustained_clock_speed_ghz=_safe_get_clock_speed(
                                instance_type_data
                            ),
                            p_cores=instance_type_data["VCpuInfo"].get(
                                "DefaultVCpus", None
                            ),
                            v_cores=instance_type_data["VCpuInfo"].get(
                                "DefaultCores", None
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
