#!/bin/bash

set -ex

poetry run mypy --config=./scripts/lint/mypy jupiter
poetry run pylint --jobs=8 --rcfile=./scripts/lint/pylint jupiter
poetry run pyflakes jupiter
poetry run bandit --configfile=./scripts/lint/bandit -r jupiter
poetry run pydocstyle --config=./scripts/lint/pydocstyle jupiter
poetry run vulture jupiter --ignore-names COUNT,MONETARY_AMOUNT,WEIGHT,icon,branch_key
