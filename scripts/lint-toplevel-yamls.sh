#!/bin/bash

set -ex

poetry run yamllint --config-file=./scripts/lint/yamllint .readthedocs.yml
poetry run yamllint --config-file=./scripts/lint/yamllint mkdocs.yml
