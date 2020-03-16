#!/bin/bash

set -e

docker run --rm -i hadolint/hadolint:latest-debian < Dockerfile