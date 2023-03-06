FROM python:3 as build
WORKDIR /src
COPY pyproject.toml Makefile /src/
COPY hubs_bot/ /src/hubs_bot/
RUN pip install --no-cache-dir --disable-pip-version-check build~=0.10.0 && \
    python -m build --wheel

FROM python:3-slim as runtime
LABEL maintainer="m@rkis.net"
CMD ["python", "-m", "hubs_bot"]
RUN adduser --disabled-password bot

COPY --from=build /src/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl

USER bot
