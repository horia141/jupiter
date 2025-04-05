#!/bin/bash

set -ex

# Check Python
(cd src/core && poetry run mypy --config=../../scripts/check/lint/mypy --package jupiter.core --package tests --explicit-package-bases --show-absolute-path)
(cd src/cli && MYPYPATH=../core poetry run mypy --config=../../scripts/check/lint/mypy --package jupiter.cli --package tests --explicit-package-bases --show-absolute-path)
(cd src/webapi && MYPYPATH=../core poetry run mypy --config=../../scripts/check/lint/mypy --package jupiter.webapi --package tests --explicit-package-bases --show-absolute-path)
poetry run ruff check --cache-dir=.build-cache/ruff --config=./scripts/check/lint/ruff.toml src itests

# Check Node+TS
(cd src/webui && npx tsc)
npx prettier --check --list-different src/webui src/desktop src/mobile
npx eslint src/webui
