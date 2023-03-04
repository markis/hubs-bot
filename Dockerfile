FROM python:3-alpine as base
LABEL maintainer="m@rkis.net"
WORKDIR /app
ENTRYPOINT ["python", "-m", "hubs_bot"]
RUN adduser --disabled-password bot

FROM base as build
RUN apk add --no-cache build-base
COPY . /app
RUN make build

FROM base as runtime
USER bot
COPY . /app
COPY --from=build /app/dist/ /tmp/
RUN pip install --user --no-cache-dir /tmp/hubs_bot-1.0.0-py3-none-any.whl 
