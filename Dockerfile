# 使用 Python 基础镜像并指定 arm64 平台
ARG PYTHON_BASE=python:3.11-slim
FROM --platform=linux/arm64/v8 $PYTHON_BASE AS builder

ENV EXTERNAL_PYPI_SERVER=https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 PDM
RUN pip install -i $EXTERNAL_PYPI_SERVER -U pdm

# 禁用更新检查
ENV PDM_CHECK_UPDATE=false

# 复制项目文件
COPY pyproject.toml pdm.lock README.md /project/

# 安装依赖和项目到本地包目录
WORKDIR /project
RUN pdm config pypi.url $EXTERNAL_PYPI_SERVER && pdm install --check --prod --no-editable

# 运行阶段
FROM --platform=linux/arm64/v8 $PYTHON_BASE AS final

# 复制已安装的依赖
COPY --from=builder /project/.venv/ /project/.venv
ENV PATH="/project/.venv/bin:$PATH"

# 安装 Redis 及其依赖
RUN apt-get update && apt-get install -y redis-server libatomic1 && apt-get clean

# 设置工作目录
RUN mkdir /workspace/
WORKDIR /workspace/
COPY . /workspace/

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -sf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

# 设置启动命令
CMD ["sh", "-c", "redis-server --daemonize yes && uvicorn main:app --host 0.0.0.0 --port 7860 --workers 3"]