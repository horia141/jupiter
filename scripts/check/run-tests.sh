#!/bin/bash

set -ex

mkdir -p .build-cache/test

# TODO(horia141): find out why the hell poetry run doesn't work here 
pytest src/core/tests --html-report=.build-cache/test/test-report.html --title="Jupiter Tests"
