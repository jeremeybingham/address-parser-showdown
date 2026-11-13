# The whole stack in one image: this project's Python environment and the pinned libpostal build.
# Build:  docker build -t address-parser-showdown .      Run:  docker run --rm address-parser-showdown tools/check.sh
# The image is large (about 3 GB of libpostal model data). Not part of CI.
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive LIBPOSTAL_HOME=/opt/libpostal
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl git build-essential autoconf automake libtool pkg-config \
    && rm -rf /var/lib/apt/lists/*
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh

WORKDIR /app
# libpostal first: it changes least, so its layer is cached
COPY tools/libpostal /app/tools/libpostal
RUN tools/libpostal/build.sh /opt/libpostal

COPY . /app
ENV LD_LIBRARY_PATH=/opt/libpostal/install/lib
RUN uv sync --frozen
CMD ["tools/check.sh"]
