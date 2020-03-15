#!/bin/bash

set -e

source Config

docker login --username="${DOCKERHUB_USER}" --password-stdin
docker tag jupiter "${DOCKERHUB_USER}"/"${BASENAME}":"${VERSION}"
docker push "${DOCKERHUB_USER}"/"${BASENAME}":"${VERSION}"
docker tag jupiter "${DOCKERHUB_USER}"/"${BASENAME}":latest
docker push "${DOCKERHUB_USER}"/"${BASENAME}":latest
