#!/bin/bash

set -ex

source src/Config.global

export PUBLIC_NAME
export AUTHOR
export COPYRIGHT

cd src/docs && mkdocs serve
