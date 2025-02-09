from typing import List

from pydantic import BaseModel
from pydantic.fields import Field


class SpotInstancePriceResponse(BaseModel):
    instance_type: str = Field(
        description="The type of the instance (e.g., `m5.xlarge`).",
        examples=["m5.xlarge"],
    )
    product_description: str | None = Field(
        description="Amazon's Product Description",
        examples=["Linux/UNIX", "Red Hat Enterprise Linux"],
    )
    price_usd_hourly: float = Field(
        description="The current hourly price in USD.", examples=[123.45]
    )
    region: str = Field(
        description="The AWS region where the instance is available.",
        examples=["us-east-1"],
    )
    availability_zone: str = Field(
        description="The specific availability zone within the region.",
        examples=["us-east-1a"],
    )
    timestamp: str = Field(
        description="The ISO 8601 timestamp when the price was recorded.",
        examples=["2024-12-14T12:34:56Z"],
    )
    v_cores: int = Field(
        description="The number of virtual CPU p_cores for the instance type.",
        examples=[4],
    )
    cores: int = Field(
        description="The number of physical CPU p_cores for the instance type.",
        examples=[2],
    )
    sustained_clock_speed_ghz: float | None = Field(
        description="The sustained clock speed of the instance type in GHz.",
        examples=[2.5],
    )
    femto_usd_per_v_core_cycle: float | None = Field(
        description="Cost per clock cycle, per V core in units of USD * 10^15",
        examples=[1.234],
    )
    femto_usd_per_p_core_cycle: float | None = Field(
        description="Cost per clock cycle, per physical core in units of USD * 10^15",
        examples=[1.234],
    )


class CurrentPricesResponse(BaseModel):
    response: List[SpotInstancePriceResponse] = Field(
        description="A list of spot instance price information.",
        examples=[
            [
                {
                    "instance_type": "m5.xlarge",
                    "product_description": "Linux/UNIX",
                    "price_usd_hourly": 123.45,
                    "region": "us-east-1",
                    "availability_zone": "us-east-1a",
                    "timestamp": "2024-12-14T12:34:56Z",
                    "v_cores": 4,
                    "p_cores": 2,
                    "sustained_clock_speed_ghz": 2.5,
                }
            ]
        ],
    )


class FilterOptions(BaseModel):
    instance_types: List[str]
    operating_systems: List[str]
    regions: List[str]


class ErrorResponse(BaseModel):
    error: str = Field(
        description="A human-readable description of the error.",
        examples=["Invalid query parameters."],
    )
    code: int = Field(description="An application-specific error code.", examples=[400])
