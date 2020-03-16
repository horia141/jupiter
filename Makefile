lint:
	./scripts/lint.sh

docker-build:
	./scripts/docker-build.sh

docker-push:
	./scripts/docker-push.sh

.PHONY: lint docker-build docker-push
