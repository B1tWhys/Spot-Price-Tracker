# Backend

This directory contains the backend code for the Spot Price Tracker project. These instructions cover setting up the backend for local development.

---

## Prerequisites

1. **Python 3.13+**:
   - Ensure Python is installed on your system.
   - [Download Python](https://www.python.org/downloads/) if needed.

2. **Poetry**:
   - Install Poetry for dependency management: https://python-poetry.org/docs/#installation

---

## Installing Dependencies

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install project dependencies with Poetry:
```bash
poetry install
```

3. Activate the virtual environment (optional, but useful for running commands directly):
```bash
poetry shell
```

4. Install pre-commit hooks
```bash
poetry run pre-commit install
```

---

## Setting Up the Database

The backend uses timescaleDB. The easiest way to get it running for development is using docker. The following shell
script will launch a timescaleDB container, and bootstrap the database schema using alembic:
```bash
./start_docker_db.sh
```