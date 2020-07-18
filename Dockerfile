FROM python:3.8-slim
LABEL maintainer='horia141@gmail.com'

RUN apt-get update && \
    apt-get install -y git=1:2.20.1-2+deb10u3 --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN git --version
WORKDIR /jupiter

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src src

ENV TZ=UTC

# ENTRYPOINT ["python", "-m", "cProfile", "-s", "time", "src/jupiter.py"]
ENTRYPOINT ["python", "src/jupiter.py"]