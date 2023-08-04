FROM python:3.11 as builder
ARG BUILD_VERSION=0.10.0

WORKDIR /src
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DISABLE_ROOT_WARNING=1 \
  PIP_ROOT_USER_ACTION=ignore

COPY pyproject.toml /src/
COPY hubs_bot/ /src/hubs_bot/
RUN pip install --no-cache-dir build~="$BUILD_VERSION"; \
  python -m build --wheel


FROM python:3.11-slim as runtime
CMD ["python", "-m", "hubs_bot"]
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DISABLE_ROOT_WARNING=1 \
  PIP_ROOT_USER_ACTION=ignore

RUN --mount=type=bind,from=builder,src=/src/dist,target=/src/dist \
  pip install --no-cache-dir /src/dist/*.whl

RUN groupadd --system --gid 888 bot && \
  useradd --system --uid 888 --no-user-group --gid 888 \
  --create-home --home-dir /home/bot --shell /bin/bash bot

USER bot
