fast-lint:
	./scripts/fast-lint.sh

test:
	./scripts/run-tests.sh

coverage:
	./scripts/run-coverage.sh

check:
	./scripts/check.sh

fix-style:
	./scripts/fix-style.sh

migration-test:
	./scripts/migration.sh

docs:
	./scripts/docs.sh

docker-build:
	./scripts/docker-build.sh

docker-push:
	./scripts/docker-push.sh

stats-for-nerds:
	./scripts/stats-for-nerds.sh

.PHONY: fast-lint test coverage check fix-style docs migration-test docker-build docker-push stats-for-nerds
