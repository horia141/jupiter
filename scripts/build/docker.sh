#!/bin/bash

set -ex

source src/Config.global

docker build -t jupiter/webapi:latest -t jupiter/webapi:${VERSION} -f src/webapi/Dockerfile .
docker build -t jupiter/webui:latest -t jupiter/webui:${VERSION} -f src/webui/Dockerfile .
docker build -t jupiter/cli:latest -t jupiter/cli:${VERSION} -f src/cli/Dockerfile .