#!/bin/bash

set -ex

docker run --rm -i hadolint/hadolint:latest-debian < Dockerfile