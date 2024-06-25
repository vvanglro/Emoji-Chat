ARG PYTHON_BASE=3.11-slim
# build stage
FROM --platform=linux/amd64 python:$PYTHON_BASE AS builder

ENV EXTERNAL_PYPI_SERVER=https://pypi.tuna.tsinghua.edu.cn/simple
# install PDM
RUN pip install -i $EXTERNAL_PYPI_SERVER -U pdm

# disable update check
ENV PDM_CHECK_UPDATE=false
# copy files
COPY pyproject.toml pdm.lock README.md /project/

# install dependencies and project into the local packages directory
WORKDIR /project
RUN pdm config pypi.url $EXTERNAL_PYPI_SERVER && pdm install --check --prod --no-editable

# run stage
FROM --platform=linux/amd64 python:$PYTHON_BASE

# retrieve packages from build stage
COPY --from=builder /project/.venv/ /project/.venv
ENV PATH="/project/.venv/bin:$PATH"
# set command/entrypoint, adapt to fit your needs
RUN mkdir /workspace/
WORKDIR /workspace/
ADD . /workspace/
ENV TZ=Asia/Shanghai
RUN ln -sf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone \
