#!/bin/bash

set -ex

mkdir -p .build-cache/itest

pytest itests --html-report=.build-cache/itest/test-report.html --title="Jupiter Integration Tests"
