FROM python:3-alpine as base
LABEL maintainer="m@rkis.net"
WORKDIR /app
ENTRYPOINT ["python", "-m", "hubs_bot.app"]

FROM base as build
RUN apk add --no-cache build-base
COPY . /app
RUN make build

FROM base as runtime
COPY --from=build /app/dist/ /tmp/
RUN pip install --no-cache-dir /tmp/hubs_bot-1.0.0-py3-none-any.whl 
