docker-build:
	docker build -t jupiter .

docker-push:
	docker tag jupiter horia141/jupiter:latest
	docker push horia141/jupiter:latest

.PHONY: docker-build docker-push
