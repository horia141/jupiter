#!/bin/bash

set -ex

mdl --config="./scripts/lint/mdl" docs/
mdl --config="./scripts/lint/mdl" README.md