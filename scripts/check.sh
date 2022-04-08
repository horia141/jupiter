#!/bin/bash

set -ex

./scripts/lint.sh
./scripts/run-tests.sh
./scripts/check-depdendency-libyear.sh
./scripts/check-all-is-black.sh
