#!/bin/bash

set -ex

BUGFIX_BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)

if [[ "${BUGFIX_BRANCH_NAME}" != bugfix/* ]]
then
    echo "Must be on a bugfix branch"
    exit 1
fi

if ! git diff --cached --exit-code --quiet
then
    echo "There are uncomitted changed"
    exit 1
fi

git checkout develop
git merge --squash "${BUGFIX_BRANCH_NAME}"
git commit -a -m "Merged branch ${BUGFIX_BRANCH_NAME} into develop"
git branch -D "${BUGFIX_BRANCH_NAME}"
git push origin develop
