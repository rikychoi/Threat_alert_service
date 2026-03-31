FROM python:3.8-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    CONFIG_FILE=files/config.ini

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        bzip2 \
        libfontconfig1 \
        libfreetype6 \
        libxrender1 \
        libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app

# Tests expect these relative paths from WORKDIR:
# - files/config.ini
# - files/phantomjs
#
# The repository's tests/files/phantomjs is not guaranteed to be a valid
# Linux binary. So we download PhantomJS during the image build.
ARG PHANTOMJS_VERSION=2.1.1
ARG PHANTOMJS_URL="https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-${PHANTOMJS_VERSION}-linux-x86_64.tar.bz2"
ARG PHANTOMJS_SHA256="86dd9a4bf4aee45f1a84c9f61cf1947c1d6dce9b9e8d2a907105da7852460d2f"

RUN mkdir -p /app/files \
    && curl -fsSL -o /tmp/phantomjs.tar.bz2 "${PHANTOMJS_URL}" \
    && echo "${PHANTOMJS_SHA256}  /tmp/phantomjs.tar.bz2" | sha256sum -c - \
    && tar -xvjf /tmp/phantomjs.tar.bz2 -C /tmp \
    && cp /tmp/phantomjs-${PHANTOMJS_VERSION}-linux-x86_64/bin/phantomjs /app/files/phantomjs \
    && chmod +x /app/files/phantomjs

CMD ["python", "run_sources.py"]
