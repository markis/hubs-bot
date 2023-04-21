FROM python:3 as builder
ARG BUILD_VERSION=0.10.0

WORKDIR /src
RUN mkdir -p /opt && python3 -m venv /opt/venv
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DISABLE_ROOT_WARNING=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PIP_CACHE_DIR=/var/cache/pip

COPY pyproject.toml Makefile /src/
COPY hubs_bot/ /src/hubs_bot/
RUN --mount=type=cache,target=/var/cache/pip/ \
    pip install build~="$BUILD_VERSION" && \
    python -m build --wheel

ENV PATH="/opt/venv/bin:$PATH" \
    VIRTUAL_ENV="/opt/venv"

RUN --mount=type=cache,target=/var/cache/pip/ \
    pip install /src/dist/*.whl

FROM python:3-slim as runtime
CMD ["python", "-m", "hubs_bot"]
ENV PATH="/opt/venv/bin:$PATH" \
    VIRTUAL_ENV="/opt/venv"

RUN groupadd --system --gid 888 bot && \
    useradd --system --uid 888 --no-user-group --gid 888 \
        --create-home --home-dir /var/lib/bot --shell /bin/bash bot

COPY --from=builder /opt/venv /opt/venv

USER bot
