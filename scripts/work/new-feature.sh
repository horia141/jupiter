#!/bin/bash

set -ex

FEATURE_NAME=$1

git checkout develop
git pull
git checkout -b "feature/${FEATURE_NAME}"
