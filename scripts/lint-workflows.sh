#!/bin/bash

set -ex

yamllint --config-file=./scripts/lint/yamllint .github/
