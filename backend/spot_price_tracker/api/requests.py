from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class CurrentPricesOrderBy(Enum):
    PRICE_USD_HOURLY = "price_usd_hourly"
    FEMTO_USD_PER_V_CORE_CYCLE = "femto_usd_per_v_core_cycle"
    FEMTO_USD_PER_P_CORE_CYCLE = "femto_usd_per_p_core_cycle"


class CurrentPricesQuery(BaseModel):
    instance_types: Optional[List[str]] = None
    operating_systems: Optional[List[str]] = None
    regions: Optional[List[str]] = None
    order_by: Optional[CurrentPricesOrderBy] = None
    ascending: Optional[bool] = True
