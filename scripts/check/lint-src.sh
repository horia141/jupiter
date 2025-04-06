#!/bin/bash

set -ex

# Python
(cd src/core && poetry run mypy --config=../../scripts/check/lint/mypy --package jupiter.core --package tests --explicit-package-bases --show-absolute-path)
(cd src/cli && MYPYPATH=../core poetry run mypy --config=../../scripts/check/lint/mypy --package jupiter.cli --package tests --explicit-package-bases --show-absolute-path)
(cd src/webapi && MYPYPATH=../core poetry run mypy --config=../../scripts/check/lint/mypy --package jupiter.webapi --package tests --explicit-package-bases --show-absolute-path)
poetry run ruff check --cache-dir=.build-cache/ruff --config=./scripts/check/lint/ruff.toml src itests
poetry run pyflakes src/core src/cli src/webapi itests
poetry run bandit --configfile=./scripts/check/lint/bandit --ini=./scripts/check/lint/bandit.src.ini -r src/core src/cli src/webapi
poetry run bandit --configfile=./scripts/check/lint/bandit --ini=./scripts/check/lint/bandit.test.ini -r itests
poetry run pydocstyle --config=./scripts/check/lint/pydocstyle src/core src/cli src/webapi itests
poetry run vulture src/core src/cli src/webapi itests \
    --exclude=migrations/ \
    --ignore-decorators=@app.post,@app.get,@app.exception_handler,@app.on_event,@app.middleware,@app.websocket \
    --ignore-names match_highlight,search_rank,sync_sqlite_db_url,COUNT,MONETARY_AMOUNT,WEIGHT,icon,branch_key,'Stub*',new_email_task,new_slack_task,EASY,MEDIUM,HARD,ACQUAINTANCE,SCHOOL_BUDDY,WORK_BUDDY,COLLEAGUE,OTHER,VACATIONS,PROJECTS,SMART_LISTS,STAGING,LOCAL,URGENT,IMPORTANT_AND_URGENT,REGULAR,IMPORTANT,HOSTED_GLOBAL,default_feature_flags,feature_hack

# TS+Node
(cd src/webui && npx tsc)
npx prettier --check src/webui src/desktop src/mobile
npx eslint src/webui
