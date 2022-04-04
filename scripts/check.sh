#!/bin/bash

set -ex

./scripts/lint.sh
./scripts/check-depdendency-libyear.sh
