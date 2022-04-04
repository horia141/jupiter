#!/bin/bash

set -ex

./scripts/lint.sh
./scripts/check-depdendency-libyear.sh
./scripts/check-all-is-black.sh
