docker-build:
	./scripts/docker-build.sh

docker-push:
	./scripts/docker-push.sh

.PHONY: docker-build docker-push
