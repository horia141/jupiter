FROM python:3.13.0
LABEL maintainer='horia141@gmail.com'

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update && \
    apt-get install -y git curl netcat-openbsd libasound2-dev --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir "pipx==1.1.0" && pipx install "poetry==2.1.1"
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.local/bin:/root/.cargo/bin:${PATH}"

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

RUN cd ../core && poetry install --only main --no-interaction --no-ansi
RUN poetry install --only main --no-interaction --no-ansi

ENTRYPOINT ["python", "-m", "jupiter.cli.jupiter"]
