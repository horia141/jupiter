#!/bin/bash

set -ex

pylint --jobs=8 --rcfile=./scripts/lint/pylint ./src
pyflakes ./src
bandit -r ./src