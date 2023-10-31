# Use a smaller base image
FROM python:3.10-slim AS builder

WORKDIR /code

# Don't write bytecode to disk to prevent `.pyc` files
ENV PYTHONDONTWRITEBYTECODE 1

# Don't store pip cache
ENV PIP_NO_CACHE_DIR=off

# Install gcc and other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc

COPY ./requirements.txt /code/requirements.txt

# Install requirements and remove unnecessary files
RUN pip install --no-cache-dir -r /code/requirements.txt

# Multi-stage build
FROM python:3.10-slim

WORKDIR /code

# Copy the entire Python install directory from the previous stage
COPY --from=builder /usr/local /usr/local

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--workers", "1", "--timeout-keep-alive", "5", "--timeout-graceful-shutdown", "15", "--port", "4000"]
# Other settings
# "--limit-max-requests", "1000"
# Alternate way to use dynamic port from environment variable
# CMD uvicorn app.main:app --proxy-headers --host 0.0.0.0 --port $PORT
