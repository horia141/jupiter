#!/bin/bash

set -ex

mdl --config="./scripts/lint/mdl-docs" docs/
mdl --config="./scripts/lint/mdl-readme" README.md