#!/bin/bash

set -e

./scripts/lint-workflows.sh
./scripts/lint-docs.sh
./scripts/lint-scripts.sh
./scripts/lint-sources.sh
