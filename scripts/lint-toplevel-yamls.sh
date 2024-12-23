#!/bin/bash

set -ex

poetry run yamllint --config-file=./scripts/lint/yamllint src/docs/mkdocs.yml
