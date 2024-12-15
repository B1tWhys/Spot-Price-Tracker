# Backend

This directory contains the backend code for the Spot Price Tracker project. These instructions cover setting up the backend for local development.

---

## Prerequisites

1. **Python 3.13+**:
   - Ensure Python is installed on your system.
   - [Download Python](https://www.python.org/downloads/) if needed.

2. **Poetry**:
   - Install Poetry for dependency management: https://python-poetry.org/docs/#installation

3. **Database**:
   - Set database connection options as an environment variable:
     ```bash
     export DATABASE_URL="sqlite:///example.db"
     ```
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

---

## Setting Up the Database

The backend uses **SQLite** for local development by default. To bootstrap a sqlite database for development, run:
```bash
poetry run alembic upgrade head
```

This will create the SQLite database (`example.db`) in the backend directory and create the schema.

---

## Notes

- If you need to re-run the migrations or reset the database, you can delete `example.db` and re-apply the migrations:
  ```bash
  rm example.db
  poetry run alembic upgrade head
  ```
```