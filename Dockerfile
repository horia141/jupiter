FROM python:3.8.5-slim
LABEL maintainer='horia141@gmail.com'

RUN apt-get update && \
    apt-get install -y git=1:2.20.1-2+deb10u3 curl=7.64.0-4+deb10u2 netcat=1.10-41.1 --no-install-recommends && \
    apt-get clean && \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py > get-poetry.py && \
    python get-poetry.py && \
    rm -rf /var/lib/apt/lists/*
ENV PATH="${PATH}:/root/.poetry/bin"

WORKDIR /jupiter

COPY pyproject.toml ./
COPY poetry.lock ./
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

COPY migrations migrations
COPY jupiter jupiter
COPY jupiter/jupiter.py jupiter.py
COPY jupiter/migrator.py migrator.py
COPY Config Config

# ENTRYPOINT ["python", "-m", "cProfile", "-s", "time", "jupiter/jupiter.py"]
WORKDIR /data
ENTRYPOINT ["python", "/jupiter/jupiter.py"]
