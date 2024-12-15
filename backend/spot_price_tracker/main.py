import typer

app = typer.Typer(help="Spot Price Tracker CLI")


def run_server():
    """
    Placeholder for the API server logic.
    """
    typer.echo("Starting the API server... (to be implemented)")


def update_data():
    """
    Placeholder for the data update logic.
    """
    typer.echo("Updating the database with new data... (to be implemented)")


# Add subcommands
app.command(name="server")(run_server)
app.command(name="update-data")(update_data)

if __name__ == "__main__":
    app()
