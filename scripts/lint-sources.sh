#!/bin/bash

set -ex

pylint --jobs=8 --rcfile=./scripts/lint/pylint ./src
pyflakes ./src
bandit --configfile=./scripts/lint/bandit -r ./src
pydocstyle --config=./scripts/lint/pydocstyle ./src
vulture ./src