FROM python:3.6-alpine
MAINTAINER Horia Coman <horia141@gmail.com>

RUN apk --no-cache --update add \
    build-base \
    libffi-dev \
    openssl-dev

WORKDIR /jupiter

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src src

ENTRYPOINT ["python", "src/jupiter.py"]
