"""Add current prices indexes

Revision ID: 750d1fb71722
Revises: 2cc80628e424
Create Date: 2024-12-27 16:16:16.772369

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "750d1fb71722"
down_revision: Union[str, None] = "2cc80628e424"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "idx_sort_v_core_cycle_price",
        "current_spot_instance_prices",
        [text("femto_usd_per_v_core_cycle ASC")],
    )
    op.create_index(
        "idx_sort_p_core_cycle_price",
        "current_spot_instance_prices",
        [text("femto_usd_per_p_core_cycle ASC")],
    )
    op.create_index(
        "idx_sort_total_price",
        "current_spot_instance_prices",
        [text("price_usd_hourly ASC")],
    )
    op.create_index(
        "idx_filter",
        "current_spot_instance_prices",
        ["instance_type", "product_description", "region"],
    )


def downgrade() -> None:
    op.drop_index("idx_sort_v_core_cycle_price")
    op.drop_index("idx_sort_p_core_cycle_price")
    op.drop_index("idx_sort_total_price")
    op.drop_index("idx_filter")
