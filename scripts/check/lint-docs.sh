#!/bin/bash

set -ex

# bundle exec TODO(horia141): fix this!
mdl --config="./scripts/check/lint/mdl-docs" docs/
mdl --config="./scripts/check/lint/mdl-docs" src/docs/
mdl --config="./scripts/check/lint/mdl-readme" README.md
mdl --config="./scripts/check/lint/mdl-readme" src/core/README.md
mdl --config="./scripts/check/lint/mdl-readme" src/cli/README.md
mdl --config="./scripts/check/lint/mdl-readme" src/webapi/README.md
mdl --config="./scripts/check/lint/mdl-readme" src/webui/README.md
mdl --config="./scripts/check/lint/mdl-readme" src/desktop/README.md
mdl --config="./scripts/check/lint/mdl-readme" itests/README.md
