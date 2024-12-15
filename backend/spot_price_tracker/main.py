import typer
import uvicorn
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


@app.command(name="update_data")
def update_data():
    """
    Placeholder for the data update logic.
    """
    typer.echo("Updating the database with new data... (to be implemented)")


@app.command(name="seed_db")
def seed_database():
    typer.echo("Seeding the database...")
    db.seed_database()
    typer.echo("Database seeded successfully")


if __name__ == "__main__":
    app()
