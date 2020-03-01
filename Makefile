include Config
export

docker-build:
	docker build -t jupiter .

docker-push:
	docker login --username=${DOCKERHUB_USER} --password-stdin
	docker tag jupiter ${DOCKERHUB_USER}/${BASENAME}:${VERSION}
	docker push ${DOCKERHUB_USER}/${BASENAME}:${VERSION}

.PHONY: docker-build docker-push
