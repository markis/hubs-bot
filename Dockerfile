FROM python:3-alpine as base
LABEL maintainer="m@rkis.net"
CMD ["python", "-m", "hubs_bot"]
RUN adduser --disabled-password bot

FROM base as build
RUN apk add --no-cache build-base
WORKDIR /src
COPY . /src
RUN make build

FROM base as runtime
USER bot
COPY --from=build /src/dist/ /tmp/
RUN pip install --user --no-cache-dir /tmp/hubs_bot-1.0.0-py3-none-any.whl
