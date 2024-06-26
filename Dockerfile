ARG PYTHON_BASE=python:3.11-slim

FROM  $PYTHON_BASE AS builder

RUN pip install -U pdm

ENV PDM_CHECK_UPDATE=false

COPY pyproject.toml pdm.lock README.md /project/

WORKDIR /project
RUN pdm install --check --prod --no-editable

FROM $PYTHON_BASE AS final

# 复制已安装的依赖
COPY --from=builder /project/.venv/ /project/.venv
ENV PATH="/project/.venv/bin:$PATH"

RUN apt-get update && apt-get install -y redis-server libatomic1 && apt-get clean

RUN mkdir /workspace/
WORKDIR /workspace/
COPY . /workspace/

ENV TZ=Asia/Shanghai
RUN ln -sf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

CMD ["sh", "-c", "redis-server --daemonize yes && uvicorn main:app --host 0.0.0.0 --port 7860 --workers 3"]
