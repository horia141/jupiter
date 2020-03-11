include Config
export

new-feature:
	./scripts/new-feature.sh

docker-build:
	docker build -t jupiter .

docker-push:
	docker login --username=${DOCKERHUB_USER} --password-stdin
	docker tag jupiter ${DOCKERHUB_USER}/${BASENAME}:${VERSION}
	docker push ${DOCKERHUB_USER}/${BASENAME}:${VERSION}
	docker tag jupiter ${DOCKERHUB_USER}/${BASENAME}:latest
	docker push ${DOCKERHUB_USER}/${BASENAME}:latest

.PHONY: new-feature docker-build docker-push
