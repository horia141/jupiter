#!/bin/bash

set -ex

poetry run mypy --config=./scripts/lint/mypy jupiter tests
poetry run pylint --jobs=8 --rcfile=./scripts/lint/pylint jupiter tests
poetry run pyflakes jupiter tests
poetry run bandit --configfile=./scripts/lint/bandit -r jupiter tests
poetry run pydocstyle --config=./scripts/lint/pydocstyle jupiter tests
poetry run vulture jupiter tests --ignore-names COUNT,MONETARY_AMOUNT,WEIGHT,icon,branch_key
