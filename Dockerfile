FROM python:3 as build
ARG BUILD_VERSION=0.10.0

WORKDIR /src
COPY pyproject.toml Makefile /src/
COPY hubs_bot/ /src/hubs_bot/
RUN pip install --no-cache-dir --disable-pip-version-check build~="$BUILD_VERSION" && \
    python -m build --wheel

FROM python:3-slim as runtime
LABEL maintainer="m@rkis.net"
CMD ["python", "-m", "hubs_bot"]

RUN adduser --disabled-password bot
COPY --from=build /src/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl

USER bot
