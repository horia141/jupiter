#!/bin/bash

set -ex

poetry run coverage run --branch --source jupiter --omit '*/__init__.py' -m unittest discover
poetry run coverage html
