#!/bin/bash

set -ex

./scripts/lint-dockerfile.sh
./scripts/lint-workflows.sh
./scripts/lint-docs.sh
./scripts/lint-scripts.sh
./scripts/lint-sources.sh