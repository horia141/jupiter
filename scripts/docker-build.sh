#!/bin/bash

set -ex

docker build -t jupiter-cli -f src/cli/Dockerfile .
docker build -t jupiter-webapi -f src/webapi/Dockerfile .
docker build -t jupiter-webui -f src/webui/Dockerfile .
docker build -t jupiter-desktop -f src/desktop/Dockerfile .
