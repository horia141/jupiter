FROM python:3.6-alpine
LABEL maintainer='horia141@gmail.com'

RUN apk --no-cache --update add \
    build-base=0.5-r1 \
    libffi-dev=3.2.1-r6 \
    openssl-dev=1.1.1d-r3

WORKDIR /jupiter

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src src

ENV TZ=UTC

ENTRYPOINT ["python", "src/jupiter.py"]
