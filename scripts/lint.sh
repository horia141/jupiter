#!/bin/bash

set -ex

./scripts/lint-dockerfile.sh
./scripts/lint-workflows.sh
./scripts/lint-toplevel-yamls.sh
./scripts/lint-docs.sh
# ./scripts/lint-scripts.sh
./scripts/lint-src.sh