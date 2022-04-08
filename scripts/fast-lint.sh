#!/bin/bash

set -ex

poetry run mypy --config=./scripts/lint/mypy jupiter tests
