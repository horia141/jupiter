#!/bin/bash

set -ex

docker run --rm -i \
  -v `(pwd)`/scripts/lint/hadolint:/hadolint \
  -v `(pwd)`/Dockerfile:/Dockerfile \
  hadolint/hadolint:latest-debian \
  hadolint \
  --config=/hadolint \
  /Dockerfile