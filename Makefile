include Config
export

docker-build:
	docker build -t jupiter .

docker-push:
	docker tag jupiter horia141/jupiter:${VERSION}
	docker push horia141/jupiter:${VERSION}

.PHONY: docker-build docker-push
