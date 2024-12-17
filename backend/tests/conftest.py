import pytest
import docker
import time
import random
import os


@pytest.fixture(scope="session")
def timescaledb_container():
    """Launch a TimescaleDB container for the testing session."""
    client = docker.from_env()

    # Pull the TimescaleDB image
    image = "timescale/timescaledb-ha:pg17"
    client.images.pull(image)

    # Start the container with dynamic port mapping
    container = client.containers.run(
        image,
        ports={"5432/tcp": None},  # Dynamically assign a host port
        detach=True,
        environment={
            "POSTGRES_PASSWORD": "password",
            "POSTGRES_USER": "user",
            "POSTGRES_DB": "postgres",  # Default database for PostgreSQL
        },
        name=f"test_timescaledb_{random.randint(1000, 9999)}",
        remove=True,  # Automatically remove the container when stopped
    )

    try:
        # Wait for the database to become ready
        for _ in range(30):  # Retry for up to 30 seconds
            logs = container.logs().decode("utf-8")
            if "database system is ready to accept connections" in logs:
                break
            time.sleep(1)
        else:
            raise RuntimeError("TimescaleDB container failed to start in time.")

        # Retrieve the dynamically assigned host port
        container.reload()  # Refresh container details
        host_port = container.attrs["NetworkSettings"]["Ports"]["5432/tcp"][0][
            "HostPort"
        ]

        # Yield the host port for tests to connect
        yield int(host_port)
    finally:
        # Stop and remove the container
        container.stop()


@pytest.fixture(scope="session")
def sqlalchemy_db_url(timescaledb_container):
    """
    Provide a SQLAlchemy-compatible database URL for the TimescaleDB container.
    The driver should be `timescaledb` but otherwise compatible with PostgreSQL.
    """
    host_port = timescaledb_container
    db_url = f"timescaledb://user:password@localhost:{host_port}/postgres"

    # Set the DATABASE_URL environment variable
    os.environ["DATABASE_URL"] = db_url

    yield db_url

    # Cleanup: remove the environment variable after the session
    del os.environ["DATABASE_URL"]
