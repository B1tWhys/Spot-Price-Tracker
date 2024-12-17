"""Initial schema

Revision ID: 74d68cdb7f6e
Revises:
Create Date: 2024-12-16 14:51:53.618885

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "74d68cdb7f6e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "instance_types",
        sa.Column("instance_type", sa.Text(), nullable=False),
        sa.Column(
            "sustained_clock_speed_ghz", sa.Numeric(precision=5, scale=3), nullable=True
        ),
        sa.Column("p_cores", sa.Integer(), nullable=False),
        sa.Column("v_cores", sa.Integer(), nullable=True),
        sa.Column(
            "p_core_cycles_per_hour",
            sa.Numeric(),
            sa.Computed(
                "p_cores * sustained_clock_speed_ghz * 3.6E12",
            ),
            nullable=True,
        ),
        sa.Column(
            "v_core_cycles_per_hour",
            sa.Numeric(),
            sa.Computed(
                "v_cores * sustained_clock_speed_ghz * 3.6E12",
            ),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("instance_type"),
    )

    op.create_table(
        "spot_instance_prices",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("instance_type", sa.Text(), nullable=False),
        sa.Column("product_description", sa.String(), nullable=True),
        sa.Column("region", sa.String(), nullable=False),
        sa.Column("availability_zone", sa.String(), nullable=False),
        sa.Column("price_usd_hourly", sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column("femto_usd_per_v_core_cycle", sa.Numeric(8, 4), nullable=True),
        sa.Column("femto_usd_per_p_core_cycle", sa.Numeric(), nullable=True),
        sa.ForeignKeyConstraint(
            ["instance_type"],
            ["instance_types.instance_type"],
        ),
        sa.PrimaryKeyConstraint("timestamp", "id"),
        timescaledb_hypertable={"time_column_name": "timestamp"},
    )
    op.create_index(
        op.f("ix_spot_instance_prices_availability_zone"),
        "spot_instance_prices",
        ["availability_zone", "timestamp"],
        unique=False,
    )
    op.create_index(
        op.f("ix_spot_instance_prices_femto_usd_per_p_core_cycle"),
        "spot_instance_prices",
        ["femto_usd_per_p_core_cycle", "timestamp"],
        unique=False,
    )
    op.create_index(
        op.f("ix_spot_instance_prices_femto_usd_per_v_core_cycle"),
        "spot_instance_prices",
        ["femto_usd_per_v_core_cycle", "timestamp"],
        unique=False,
    )
    op.create_index(
        op.f("ix_spot_instance_prices_instance_type"),
        "spot_instance_prices",
        ["instance_type", "timestamp"],
        unique=False,
    )
    op.create_index(
        op.f("ix_spot_instance_prices_product_description"),
        "spot_instance_prices",
        ["product_description", "timestamp"],
        unique=False,
    )
    op.create_index(
        op.f("ix_spot_instance_prices_region"),
        "spot_instance_prices",
        ["region", "timestamp"],
        unique=False,
    )
    op.execute(
        "SELECT set_chunk_time_interval('spot_instance_prices', INTERVAL '24 hours')"
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_spot_instance_prices_region"), table_name="spot_instance_prices"
    )
    op.drop_index(
        op.f("ix_spot_instance_prices_product_description"),
        table_name="spot_instance_prices",
    )
    op.drop_index(
        op.f("ix_spot_instance_prices_instance_type"), table_name="spot_instance_prices"
    )
    op.drop_index(
        op.f("ix_spot_instance_prices_femto_usd_per_v_core_cycle"),
        table_name="spot_instance_prices",
    )
    op.drop_index(
        op.f("ix_spot_instance_prices_femto_usd_per_p_core_cycle"),
        table_name="spot_instance_prices",
    )
    op.drop_index(
        op.f("ix_spot_instance_prices_availability_zone"),
        table_name="spot_instance_prices",
    )
    op.drop_table("spot_instance_prices")
    op.drop_table("instance_types")
