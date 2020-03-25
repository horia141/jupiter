lint:
	./scripts/lint.sh

docs:
	./scripts/docs.sh

docker-build:
	./scripts/docker-build.sh

docker-push:
	./scripts/docker-push.sh

.PHONY: lint docs docker-build docker-push
