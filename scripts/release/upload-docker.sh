#!/bin/bash

set -ex

source src/Config.global

docker tag jupiter/webapi:latest horia141/jupiter-webapi:latest
docker tag jupiter/webapi:${VERSION} horia141/jupiter-webapi:${VERSION}
docker tag jupiter/webui:latest horia141/jupiter-webui:latest
docker tag jupiter/webui:${VERSION} horia141/jupiter-webui:${VERSION}
docker tag jupiter/cli:latest horia141/jupiter-cli:latest
docker tag jupiter/cli:${VERSION} horia141/jupiter-cli:${VERSION}

docker image push horia141/jupiter-webapi:latest
docker image push horia141/jupiter-webapi:${VERSION}
docker image push horia141/jupiter-webui:latest
docker image push horia141/jupiter-webui:${VERSION}
docker image push horia141/jupiter-cli:latest
docker image push horia141/jupiter-cli:${VERSION}
