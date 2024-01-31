FROM python:3.11 as builder
ARG BUILD_VERSION=0.10.0

WORKDIR /src
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DISABLE_ROOT_WARNING=1 \
  PIP_ROOT_USER_ACTION=ignore \
  PIP_CACHE_DIR="/var/cache/pip/" \
  HATCH_BUILD_HOOK_ENABLE_MYPYC=1

COPY pyproject.toml /src/
COPY hubs_bot/ /src/hubs_bot/
RUN --mount=type=cache,target=/var/cache/pip/ \
  --mount=type=bind,src=.git,dst=/src/.git \
  pip install --no-cache-dir build~="$BUILD_VERSION"; \
  python -m build --wheel


FROM python:3.11-slim as runtime
CMD ["run_hubs_bot"]
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DISABLE_ROOT_WARNING=1 \
  PIP_ROOT_USER_ACTION=ignore \
  PIP_CACHE_DIR="/var/cache/pip/" \
  HATCH_BUILD_HOOK_ENABLE_MYPYC=1

RUN groupadd --system --gid 888 bot && \
  useradd --system --uid 888 --no-user-group --gid 888 \
  --create-home --home-dir /home/bot --shell /bin/bash bot

ARG BUILD_ESSENTIAL=12.9
RUN --mount=type=bind,from=builder,src=/src/dist,target=/src/dist \
  --mount=type=cache,target=/var/lib/apt/lists \
  --mount=type=cache,target=/var/cache \
  --mount=type=tmpfs,target=/var/log \
  apt-get update; \
  apt-get install -y --no-install-recommends build-essential="$BUILD_ESSENTIAL"; \
  pip install --no-cache-dir /src/dist/*.whl; \
  apt-get purge -y build-essential; \
  apt-get autoremove -y;

USER bot
