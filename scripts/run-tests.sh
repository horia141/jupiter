#!/bin/bash

set -ex

poetry run python -m unittest discover
