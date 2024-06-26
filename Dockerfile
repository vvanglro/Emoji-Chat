FROM  python:3.11-slim AS builder

RUN pip install -U pdm

ENV PDM_CHECK_UPDATE=false

COPY pyproject.toml pdm.lock README.md /project/

WORKDIR /project
RUN pdm install --check --prod --no-editable

FROM ubuntu:20.04

COPY --from=builder /project/.venv/ /project/.venv
ENV PATH="/project/.venv/bin:$PATH"

RUN apt-get update && apt-get install -y redis-server libatomic1 && apt-get clean

RUN mkdir /workspace/
WORKDIR /workspace/
COPY . /workspace/

RUN mkdir -p /etc/lib/redis
RUN chmod -R 777 /etc/lib/redis

COPY redis.conf /etc/redis/redis.conf

CMD ["sh", "-c", "redis-server /etc/redis/redis.conf --daemonize yes && python -m uvicorn main:app --host 0.0.0.0 --port 7860 --workers 3"]
