#!/bin/bash

set -ex

libyear toml pyproject.toml
libyear toml src/core/pyproject.toml
libyear toml src/cli/pyproject.toml
libyear toml src/webapi/pyproject.toml
libyear toml src/docs/pyproject.toml
libyear toml itests/pyproject.toml

npx libyear
(cd src/webui && npx libyear)
(cd src/desktop && npx libyear)
(cd src/mobile && npx libyear)
