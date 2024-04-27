#!/bin/bash

set -ex

./scripts/lint.sh
./scripts/check-all-is-formatted.sh
./scripts/run-tests.sh
# ./scripts/run-itests.sh ci
