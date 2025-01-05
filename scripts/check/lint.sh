#!/bin/bash

set -ex

# ./scripts/check/lint-dockerfile.sh
./scripts/check/lint-workflows.sh
./scripts/check/lint-toplevel-yamls.sh
./scripts/check/lint-docs.sh
# ./scripts/check/lint-scripts.sh
./scripts/check/lint-src.sh
