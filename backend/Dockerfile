FROM python:3.13-alpine

WORKDIR /work

# Install deps first
RUN apk add --no-cache libpq-dev g++ linux-headers musl-dev && pip install --no-cache-dir poetry
ADD pyproject.toml .
RUN poetry install --no-cache --no-root

ADD README.md alembic.ini ./
ADD ./alembic /work/alembic
ADD ./spot_price_tracker /work/spot_price_tracker
RUN poetry install --no-cache

ENTRYPOINT ["poetry", "run"]