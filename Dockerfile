FROM python:3-alpine as hubs_bot
MAINTAINER m@rkis.cc
WORKDIR /app
ENTRYPOINT python -m hubs_bot.app 

# Install pip dependencies and avoid
# docker layer caching invalidation
ADD ./requirements.txt /app/
RUN apk add build-base && \
    pip install --no-cache --upgrade pip setuptools && \
    pip install -r requirements.txt && \
    apk del build-base && \
    rm -rf /tmp/*

ADD . .
