FROM python:3 as build
ARG BUILD_VERSION=0.10.0

WORKDIR /src
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DISABLE_ROOT_WARNING=1 \
    PIP_ROOT_USER_ACTION=ignore
COPY pyproject.toml Makefile /src/
COPY hubs_bot/ /src/hubs_bot/
RUN \
    --mount=type=cache,target=/root/.cache/ \
    pip install build~="$BUILD_VERSION" && \
    python -m build --wheel

FROM python:3-slim as runtime
CMD ["python", "-m", "hubs_bot"]
WORKDIR /src
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DISABLE_ROOT_WARNING=1 \
    PIP_ROOT_USER_ACTION=ignore

RUN adduser --disabled-password bot
COPY --from=build /src/dist/*.whl /tmp/
RUN \
    --mount=type=cache,target=/var/lib/apt/lists/ \
    --mount=type=cache,target=/var/cache/ \
    --mount=type=cache,target=/root/.cache/ \
    apt-get update && \
    apt-get install -y build-essential && \
    pip install /tmp/*.whl && \
    apt-get purge -y --auto-remove build-essential

USER bot
