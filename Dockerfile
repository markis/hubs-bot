FROM python:3 as build
WORKDIR /src
COPY pyproject.toml Makefile /src/
COPY hubs_bot/ /src/hubs_bot/
RUN make build

FROM python:3-slim as runtime
LABEL maintainer="m@rkis.net"
CMD ["python", "-m", "hubs_bot"]
RUN adduser --disabled-password bot
USER bot

COPY --from=build /src/dist/*.whl /tmp/
RUN pip install --user --no-cache-dir /tmp/*.whl
