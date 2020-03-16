#!/bin/bash

set -e

./scripts/lint-workflows.sh
./scripts/lint-scripts.sh
./scripts/lint-sources.sh
