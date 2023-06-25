#!/bin/bash

set -ex

poetry run yamllint --config-file=./scripts/lint/yamllint .github/
