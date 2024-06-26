FROM ubuntu:20.04 AS builder

# Install Python, PDM, and build dependencies
RUN apt-get update && apt-get install -y python3-pip python3-venv build-essential clang libssl-dev curl

# Install the latest version of Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:$PATH"

# Ensure Rust is updated to the latest version
RUN rustup update

RUN pip3 install -U pdm

ENV PDM_CHECK_UPDATE=false

COPY pyproject.toml pdm.lock README.md /project/

WORKDIR /project
RUN pdm install --check --prod --no-editable

FROM ubuntu:20.04

# Copy the virtual environment from the builder stage
COPY --from=builder /project/.venv/ /project/.venv
ENV PATH="/project/.venv/bin:$PATH"

# Install Redis and other dependencies
RUN apt-get update && apt-get install -y redis-server libatomic1 && apt-get clean

# Ensure redis.conf has the correct permissions and ownership
COPY redis.conf /etc/redis/redis.conf
RUN chown root:root /etc/redis/redis.conf && chmod 644 /etc/redis/redis.conf

# Prepare the workspace
RUN mkdir /workspace/
WORKDIR /workspace/
COPY . /workspace/

# Ensure redis server can run properly
RUN mkdir -p /etc/lib/redis
RUN chmod -R 777 /etc/lib/redis

# Debugging step: Verify permissions
RUN ls -l /etc/redis/

CMD ["sh", "-c", "redis-server /etc/redis/redis.conf --daemonize yes && uvicorn main:app --host 0.0.0.0 --port 7860 --workers 3"]
