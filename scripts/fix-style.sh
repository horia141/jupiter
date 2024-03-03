#!/bin/bash

set -ex

poetry run autoflake --config=scripts/lint/autoflake src/core src/cli src/webapi tests
poetry run black src/core src/cli src/webapi tests
poetry run ruff --cache-dir=.build-cache/ruff --config=./scripts/lint/ruff.toml src tests --fix
npx prettier --write src/webui --list-different src/desktop
npx eslint src/webui --fix
