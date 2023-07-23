#!/bin/bash

set -ex

# Python
(cd src/core && poetry run mypy --config=../../scripts/lint/mypy --package jupiter.core --package tests --explicit-package-bases)
(cd src/cli && MYPYPATH=../core poetry run mypy --config=../../scripts/lint/mypy --package jupiter.cli --package tests --explicit-package-bases)
(cd src/webapi && MYPYPATH=../core poetry run mypy --config=../../scripts/lint/mypy --package jupiter.webapi --package tests --explicit-package-bases)
poetry run ruff --cache-dir=.build-cache/ruff --config=./scripts/lint/ruff.toml src tests
poetry run pyflakes src/core src/cli src/webapi tests
poetry run bandit --configfile=./scripts/lint/bandit --ini=./scripts/lint/bandit.src.ini -r src/core src/cli src/webapi
poetry run bandit --configfile=./scripts/lint/bandit --ini=./scripts/lint/bandit.test.ini -r tests
poetry run pydocstyle --config=./scripts/lint/pydocstyle src/core src/cli src/webapi tests
poetry run vulture src/core src/cli src/webapi tests \
    --exclude=migrations/ \
    --ignore-decorators=@app.post,@app.get,@app.exception_handler,@app.on_event,@app.middleware,@app.websocket \
    --ignore-names sync_sqlite_db_url,COUNT,MONETARY_AMOUNT,WEIGHT,icon,branch_key,'Stub*',new_email_task,new_slack_task,EASY,MEDIUM,HARD,ACQUAINTANCE,SCHOOL_BUDDY,WORK_BUDDY,COLLEAGUE,OTHER,VACATIONS,PROJECTS,SMART_LISTS,STAGING,LOCAL,URGENT,IMPORTANT_AND_URGENT,REGULAR,IMPORTANT,HOSTED_GLOBAL,default_feature_flags,feature_hack

# TS+Node
(cd src/webui && npx tsc)
# (cd src/desktop && npx tsc) # TODO(horia141): fix this
npx eslint src/webui # src/desktop # TODO(horia141): fix this
