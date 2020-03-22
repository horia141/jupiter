#!/bin/bash

set -ex

BUGFIX_NAME=$1

git checkout develop
git pull
git checkout -b "bugfix/${BUGFIX_NAME}"
