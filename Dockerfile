FROM python:3.9-slim AS builder

ARG POETRY_VERSION=1.1.13

# Disable stdout/stderr buggering, can cause issues with Docker logs
ENV PYTHONUNBUFFERED=1

# Disable some obvious pip functionality
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_NO_CACHE_DIR=1

# Configure poetry
ENV POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_PATH=/venvs

RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean

# Install Poetry and create venv
# hadolint ignore=DL3013
RUN pip install -U pip wheel setuptools && \
  pip install "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

#
# runtime
#

FROM builder AS runtime

RUN poetry install --no-dev --remove-untracked

COPY . /app/

CMD ["poetry", "run", "iscc-observer-evm"]
