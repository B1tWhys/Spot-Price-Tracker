from datetime import datetime, timedelta, timezone
from typing import Optional, List
from more_itertools import chunked
from multiprocessing.pool import ThreadPool

import typer
import uvicorn
from sqlalchemy.orm import Session

from spot_price_tracker import aws
from spot_price_tracker.aws import RegionalSpotPriceHistoryQuery
from spot_price_tracker.db import db

app = typer.Typer(help="Spot Price Tracker CLI")


@app.command(name="server")
def run_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = True,
):
    """
    Launch the FastAPI server using Uvicorn.
    """
    typer.echo(f"Starting the server at http://{host}:{port}")
    uvicorn.run(
        "spot_price_tracker.api.web:api",
        host=host,
        port=port,
        reload=reload,
    )


@app.command(name="update-data")
def update_data(
    start_days_ago: Optional[int] = typer.Option(
        30,
        "--start-days-ago",
        help="Maximum number of days before today to start fetching data. AWS is only actually queried in each region "
        "starting from the latest timestamp we have in the DB for that region, or this offset if we don't have any"
        "data for the region yet or that was more than [start-days-ago] days ago",
    ),
    end_days_ago: Optional[int] = typer.Option(
        None,
        "--end-days-ago",
        help="Number of days before today to stop fetching data. Defaults to now (0 days ago).",
    ),
    regions: Optional[List[str]] = typer.Option(
        None,
        "--regions",
        "-r",
        help="A list of AWS regions to query. Defaults to all regions if not specified.",
    ),
    threads: int = typer.Option(
        5,
        "--threads",
        "-t",
        help="Number of threads to use when querying AWS for spot pricing data",
    ),
):
    """
    Update the database with new spot price data.
    """
    typer.echo("Starting the update process...")

    now = datetime.now(timezone.utc)
    end_time = now - timedelta(days=end_days_ago or 0)
    start_time = now - timedelta(days=start_days_ago)

    session: Session = next(db.get_db())

    try:
        # Determine the regions to query
        if not regions:
            regions = aws.get_aws_regions()
            typer.echo(f"No regions specified, defaulting to all regions: {regions}")

        region_start_times = db.get_latest_timestamps_by_region(session)
        queries = []
        for region in regions:
            region_start_time = max(
                start_time, region_start_times.get(region, start_time)
            )
            queries.append(
                RegionalSpotPriceHistoryQuery(
                    region_name=region,
                    start_time=region_start_time,
                    end_time=end_time,
                )
            )

        instance_types = db.get_all_instance_types(session)
        missing_types = []
        with ThreadPool(threads) as pool:
            for batch in pool.imap(aws.get_instance_types, regions):
                for instance_type in batch:
                    if instance_type.instance_type not in instance_types:
                        missing_types.append(instance_type)
                        instance_types[instance_type.instance_type] = instance_type
        if missing_types:
            session.add_all(missing_types)
            session.commit()

        # Fetch spot price data for all regions
        typer.echo(f"Fetching spot price data for regions: {regions}")
        for chunk_i, spot_price_chunk in enumerate(
            chunked(aws.get_spot_price_history(queries, instance_types, threads), 2000)
        ):
            typer.echo(f"Saving chunk {chunk_i}")
            session.bulk_save_objects(spot_price_chunk)
            session.commit()
            session.expunge_all()
            typer.echo(f"Chunk {chunk_i} saved")

        typer.echo("Update process completed successfully!")
    except Exception as e:
        typer.echo(f"An error occurred: {e}")
        session.rollback()
        raise e
    finally:
        session.close()


@app.command(name="seed_db")
def seed_database():
    typer.echo("Seeding the database...")
    db.seed_database()
    typer.echo("Database seeded successfully")


if __name__ == "__main__":
    app()
