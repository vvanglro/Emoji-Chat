FROM ubuntu:20.04

# Install Redis and other dependencies
RUN apt-get update && apt-get install -y redis-server libatomic1 && apt-get clean

# Copy the virtual environment from the builder stage
COPY --from=builder /project/.venv/ /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

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

# Ensure correct permissions for the virtual environment
RUN chmod -R 755 /opt/venv

# Debugging step: Verify permissions and user ID
RUN ls -l /etc/redis/ && ls -l /opt/venv/bin/ && id

CMD ["sh", "-c", "redis-server /etc/redis/redis.conf --daemonize yes && /opt/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 7860 --workers 3"]
