fast-lint:
	./scripts/fast-lint.sh

check:
	./scripts/check.sh

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

.PHONY: fast-lint check docs migration-test docker-build docker-push stats-for-nerds
