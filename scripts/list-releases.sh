#!/bin/bash

set -e

git pull --ff-only --tags origin develop
git tag --list
