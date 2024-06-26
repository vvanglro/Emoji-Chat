FROM ubuntu:20.04

RUN apt-get update && apt-get install -y redis-server pip libatomic1 && apt-get clean

RUN pip install -U pdm

ENV PDM_CHECK_UPDATE=false

RUN mkdir -p /etc/lib/redis
RUN chmod -R 777 /etc/lib/redis

COPY redis.conf /etc/redis/redis.conf

RUN mkdir /workspace/
WORKDIR /workspace/
COPY . /workspace/

RUN pdm install --check --prod --no-editable
ENV PATH="/project/.venv/bin:$PATH"

CMD ["sh", "-c", "redis-server /etc/redis/redis.conf --daemonize yes && uvicorn main:app --host 0.0.0.0 --port 7860 --workers 3"]
