#!/bin/bash

set -ex

CURRENT_BRANCH=$(git branch --show-current)

if [[ "$CURRENT_BRANCH" =~ "release/" ]]
then
  BUILDINFO_ROOT="buildinfo/${CURRENT_BRANCH}"
else
  BUILDINFO_ROOT="buildinfo/current"
fi
COVERAGE_BUILDINFO="${BUILDINFO_ROOT}/coverage"
TESTREPORT_BUILDINFO="${BUILDINFO_ROOT}/test"

rm -f .build-cache/itest/coverage/coverage.*
COLLECT_COVERAGE=TRUE pytest tests/integration/crud/ --html-report="${TESTREPORT_BUILDINFO}" --title="Jupiter Tests"
coverage combine --rcfile=scripts/coveragerc
coverage html --rcfile=scripts/coveragerc
rm -rf "${COVERAGE_BUILDINFO}"
mv .build-cache/itest/coverage-html "${COVERAGE_BUILDINFO}"
