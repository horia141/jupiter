#!/bin/bash

set -e

FEATURE_NAME=$1

git checkout develop
git pull
git checkout -b "feature/${FEATURE_NAME}"
