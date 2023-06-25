#!/bin/bash

set -ex

./scripts/lint.sh
./scripts/run-tests.sh
./scripts/check-all-is-formatted.sh
