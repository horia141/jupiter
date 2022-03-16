#!/bin/bash

set -ex

mypy --config=./scripts/lint/mypy jupiter
