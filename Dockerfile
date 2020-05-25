FROM python:3.8-slim
LABEL maintainer='horia141@gmail.com'

WORKDIR /jupiter

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src src

ENV TZ=UTC

# ENTRYPOINT ["python", "-m", "cProfile", "-s", "time", "src/jupiter.py"]
ENTRYPOINT ["python", "src/jupiter.py"]