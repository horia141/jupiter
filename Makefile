lint:
	./scripts/lint.sh

docs:
	./scripts/docs.sh

docker-build:
	./scripts/docker-build.sh

docker-push:
	./scripts/docker-push.sh

stats-for-nerds:
	./scripts/stats-for-nerds.sh

.PHONY: lint docs docker-build docker-push stats-for-nerds
