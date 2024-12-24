#!/bin/bash

set -ex

FEATURE_BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)

if [[ "${FEATURE_BRANCH_NAME}" != feature/* ]]
then
    echo "Must be on a feature branch"
    exit 1
fi

if ! git diff --cached --exit-code --quiet
then
    echo "There are uncomitted changed"
    exit 1
fi

git checkout develop
git merge --squash "${FEATURE_BRANCH_NAME}"
git commit -a -m "Merged branch ${FEATURE_BRANCH_NAME} into develop"
git branch -D "${FEATURE_BRANCH_NAME}"
git push origin develop
