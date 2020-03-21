#!/bin/bash

set -ex

pylint --jobs=8 ./src
pyflakes ./src
bandit -r ./src