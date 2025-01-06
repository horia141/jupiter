#!/bin/bash

set -ex

poetry run yamllint --config-file=./scripts/check/lint/yamllint .github/
