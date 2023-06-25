fast-lint:
	./scripts/fast-lint.sh

test:
	./scripts/run-tests.sh

itest:
	./scripts/run-integration-tests.sh

check:
	./scripts/check.sh

fix-style:
	./scripts/fix-style.sh

gen:
	./scripts/generate-client-code.sh

migration-test:
	./scripts/migration.sh

docs:
	./scripts/docs.sh

docker-build:
	./scripts/docker-build.sh

docker-push:
	./scripts/docker-push.sh

standalone-binary-build:
	./scripts/standalone-binary-build.sh

stats-for-nerds:
	./scripts/stats-for-nerds.sh

.PHONY: fast-lint test itest coverage check fix-style gen docs migration-test docker-build docker-push standalone-binary-build stats-for-nerds
