FROM python:3.13.0
LABEL maintainer='horia141@gmail.com'

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update && \
    apt-get install -y git curl netcat-openbsd dumb-init --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir "pipx==1.1.0" && pipx install "poetry==2.1.1"
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.local/bin:/root/.cargo/bin:${PATH}"

WORKDIR /jupiter

ENV VIRTUAL_ENV=/jupiter/venv
RUN python -m venv /jupiter/venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

COPY LICENSE LICENSE
COPY src/Config.global src/Config.global
COPY src/core/README.md src/core/README.md
COPY src/core/pyproject.toml src/core/pyproject.toml
COPY src/core/poetry.lock src/core/poetry.lock
COPY src/core/jupiter src/core/jupiter
COPY src/core/migrations src/core/migrations
COPY src/webapi/README.md src/webapi/README.md
COPY src/webapi/pyproject.toml src/webapi/pyproject.toml
COPY src/webapi/poetry.lock src/webapi/poetry.lock
COPY src/webapi/Config.project.live src/webapi/Config.project
COPY src/webapi/jupiter src/webapi/jupiter

WORKDIR /jupiter/src/webapi

RUN cd ../core && poetry install --only main --no-interaction --no-ansi
RUN poetry install --only main --no-interaction --no-ansi

ARG PORT=10000
ENV HOST=0.0.0.0
ENV PORT=$PORT
EXPOSE $PORT

ENTRYPOINT [ "dumb-init", "python", "-m", "jupiter.webapi.jupiter" ]
