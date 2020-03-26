#!/bin/bash

set -ex

yamllint --config-file=./scripts/lint/yamllint .readthedocs.yml
yamllint --config-file=./scripts/lint/yamllint mkdocs.yml