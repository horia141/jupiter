#!/bin/bash

set -ex

RELEASE_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if ! [[ "${RELEASE_BRANCH}" =~ "release/" ]]
then
    echo "Must be in a release"
    exit 1
fi

BUILDINFO_ROOT="buildinfo/${RELEASE_BRANCH}"
CLOC_BUILDINFO="${BUILDINFO_ROOT}/cloc"
COVERAGE_BUILDINFO="${BUILDINFO_ROOT}/coverage"
TEST_BUILDINFO="${BUILDINFO_ROOT}/test"

if ! [[ -f "${CLOC_BUILDINFO}" ]]
then
    echo "No cloc information! Please run make stats-for-nerds to fix."
    exit 1
fi

if ! [[ -d "${COVERAGE_BUILDINFO}" ]]
then
    echo "No coverage information! Please run make itest to fix."
    exit 1
fi

if ! [[ -d "${TEST_BUILDINFO}" ]]
then
    echo "No test information! Please run make itest to fix."
    exit 1
fi

RELEASE_VERSION=${RELEASE_BRANCH/release\/}

git commit -a -m "Prepared release version ${RELEASE_VERSION}"

# Merge into master
git checkout master
git merge --squash "${RELEASE_BRANCH}" --strategy recursive --strategy-option theirs
git commit -a -m "Release version ${RELEASE_VERSION}"
git tag -a "${RELEASE_VERSION}" -m "Version ${RELEASE_VERSION}"
git push --follow-tags origin master

# Merge into develop
git checkout develop
git merge master -m "Merge master with release ${RELEASE_VERSION} back into develop" --strategy recursive --strategy-option theirs
git push origin develop

# Remove old branch
git branch -D "${RELEASE_BRANCH}"
