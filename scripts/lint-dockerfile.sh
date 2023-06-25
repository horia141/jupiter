#!/bin/bash

set -ex

docker run --rm -i \
  -v "$(pwd)/scripts/lint/hadolint":/hadolint \
  -v "$(pwd)/src/cli/Dockerfile:/Dockerfile" \
  hadolint/hadolint:latest-debian \
  hadolint \
  --config=/hadolint \
  /Dockerfile

docker run --rm -i \
  -v "$(pwd)/scripts/lint/hadolint":/hadolint \
  -v "$(pwd)/src/webapi/Dockerfile:/Dockerfile" \
  hadolint/hadolint:latest-debian \
  hadolint \
  --config=/hadolint \
  /Dockerfile

docker run --rm -i \
  -v "$(pwd)/scripts/lint/hadolint":/hadolint \
  -v "$(pwd)/src/webui/Dockerfile:/Dockerfile" \
  hadolint/hadolint:latest-debian \
  hadolint \
  --config=/hadolint \
  /Dockerfile

# TODO(horia141): dockerize electron app

# docker run --rm -i \
#   -v "$(pwd)/scripts/lint/hadolint":/hadolint \
#   -v "$(pwd)/src/desktop/Dockerfile:/Dockerfile" \
#   hadolint/hadolint:latest-debian \
#   hadolint \
#   --config=/hadolint \
#   /Dockerfile
