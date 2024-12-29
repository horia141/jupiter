FROM python:3.10.8
LABEL maintainer='horia141@gmail.com'

# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get install -y git curl netcat --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir "pipx==1.1.0" && pipx install "poetry==1.3.1"
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /jupiter

ENV VIRTUAL_ENV=/jupiter/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

COPY LICENSE LICENSE
COPY src/Config.global src/Config.global
COPY src/core/README.md src/core/README.md
COPY src/core/pyproject.toml src/core/pyproject.toml
COPY src/core/poetry.lock src/core/poetry.lock
COPY src/core/migrations src/core/migrations
COPY src/core/jupiter src/core/jupiter
COPY src/cli/README.md src/cli/README.md
COPY src/cli/pyproject.toml src/cli/pyproject.toml
COPY src/cli/poetry.lock src/cli/poetry.lock
COPY src/cli/Config.project.live src/cli/Config.project
COPY src/cli/jupiter src/cli/jupiter

WORKDIR /jupiter/src/cli

RUN poetry install --only main --no-interaction --no-ansi

ENTRYPOINT ["python", "-m", "jupiter.cli.jupiter"]
