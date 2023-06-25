#!/bin/bash

set -ex

source src/Config.global
docker login --username="${DOCKERHUB_USER}" --password-stdin

source src/cli/Config.project

docker tag jupiter-cli "${DOCKERHUB_USER}"/"${BASENAME}":"${VERSION}"
docker push "${DOCKERHUB_USER}"/"${BASENAME}":"${VERSION}"
docker tag jupiter-cli "${DOCKERHUB_USER}"/"${BASENAME}":latest
docker push "${DOCKERHUB_USER}"/"${BASENAME}":latest

source src/webapi/Config.project

docker tag jupiter-webapi "${DOCKERHUB_USER}"/"${BASENAME}":"${VERSION}"
docker push "${DOCKERHUB_USER}"/"${BASENAME}":"${VERSION}"
docker tag jupiter-webapi "${DOCKERHUB_USER}"/"${BASENAME}":latest
docker push "${DOCKERHUB_USER}"/"${BASENAME}":latest

source src/webui/Config.project

docker tag jupiter-webui "${DOCKERHUB_USER}"/"${BASENAME}":"${VERSION}"
docker push "${DOCKERHUB_USER}"/"${BASENAME}":"${VERSION}"
docker tag jupiter-webui "${DOCKERHUB_USER}"/"${BASENAME}":latest
docker push "${DOCKERHUB_USER}"/"${BASENAME}":latest

source src/desktop/Config.project

docker tag jupiter-desktop "${DOCKERHUB_USER}"/"${BASENAME}":"${VERSION}"
docker push "${DOCKERHUB_USER}"/"${BASENAME}":"${VERSION}"
docker tag jupiter-desktop "${DOCKERHUB_USER}"/"${BASENAME}":latest
docker push "${DOCKERHUB_USER}"/"${BASENAME}":latest
