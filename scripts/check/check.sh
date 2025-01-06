#!/bin/bash

set -ex

./scripts/check/lint.sh
./scripts/check/check-all-is-formatted.sh
./scripts/check/run-tests.sh
./scripts/check/run-itests.sh ci
