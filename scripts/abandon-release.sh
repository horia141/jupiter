#!/bin/bash

set -e

RELEASE_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if ! [[ "${RELEASE_BRANCH}" =~ "release/" ]]
then
    echo "Must be in a release"
    exit 1
fi

git checkout -- .
git reset --hard HEAD
git checkout develop
git branch -D "${RELEASE_BRANCH}"
