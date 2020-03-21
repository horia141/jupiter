#!/bin/bash

set -ex

git pull --ff-only --tags origin develop
git tag --list
