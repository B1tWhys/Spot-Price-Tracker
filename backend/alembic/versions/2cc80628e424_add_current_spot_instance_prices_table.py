"""Add current_spot_instance_prices table

Revision ID: 2cc80628e424
Revises: 74d68cdb7f6e
Create Date: 2024-12-17 17:50:18.461278

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2cc80628e424"
down_revision: Union[str, None] = "74d68cdb7f6e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "current_spot_instance_prices",
        sa.Column("instance_type", sa.Text(), nullable=False),
        sa.Column("product_description", sa.String(), nullable=True),
        sa.Column("availability_zone", sa.String(), nullable=False),
        sa.Column("region", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("price_usd_hourly", sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column("femto_usd_per_v_core_cycle", sa.Numeric(8, 4), nullable=True),
        sa.Column("femto_usd_per_p_core_cycle", sa.Numeric(), nullable=True),
        sa.ForeignKeyConstraint(
            ["instance_type"],
            ["instance_types.instance_type"],
        ),
        sa.PrimaryKeyConstraint(
            "instance_type", "product_description", "availability_zone"
        ),
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_current_spot_instance_prices()
            RETURNS TRIGGER AS
        $$
        BEGIN
            INSERT INTO current_spot_instance_prices (instance_type, product_description, availability_zone, region, timestamp,
                                                      price_usd_hourly, femto_usd_per_v_core_cycle, femto_usd_per_p_core_cycle)
            VALUES (NEW.instance_type, NEW.product_description, NEW.availability_zone, NEW.region, NEW.timestamp,
                    NEW.price_usd_hourly, NEW.femto_usd_per_v_core_cycle, NEW.femto_usd_per_p_core_cycle)
            ON CONFLICT (instance_type, product_description, availability_zone) DO UPDATE SET price_usd_hourly           = EXCLUDED.price_usd_hourly,
                                                                                              timestamp                  = EXCLUDED.timestamp,
                                                                                              femto_usd_per_v_core_cycle = EXCLUDED.femto_usd_per_v_core_cycle,
                                                                                              femto_usd_per_p_core_cycle = EXCLUDED.femto_usd_per_p_core_cycle
            WHERE current_spot_instance_prices.timestamp < EXCLUDED.timestamp;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
    """  # noqa: E501
    )

    op.execute(
        """
        CREATE TRIGGER update_current_spot_instance_prices
            AFTER INSERT
            ON historical_spot_instance_prices
            FOR EACH ROW
        EXECUTE FUNCTION update_current_spot_instance_prices();
    """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS update_current_spot_instance_prices ON historical_spot_instance_prices"
    )
    op.execute("DROP FUNCTION IF EXISTS update_current_spot_instance_prices")
    op.drop_table("current_spot_instance_prices")
