#!/bin/bash

set -ex

mypy --config=./scripts/lint/mypy jupiter
pylint --jobs=8 --rcfile=./scripts/lint/pylint jupiter
pyflakes jupiter
bandit --configfile=./scripts/lint/bandit -r jupiter
pydocstyle --config=./scripts/lint/pydocstyle jupiter
vulture jupiter --ignore-names COUNT,MONETARY_AMOUNT,WEIGHT,icon,branch_key