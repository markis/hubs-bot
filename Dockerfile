FROM python:3-alpine as hubs_bot
MAINTAINER m@rkis.cc
WORKDIR /app

# crond doesn't like being launched directly
# this will use a shell script to launch it
RUN echo "crond -f" > ./entrypoint.sh && chmod +x ./entrypoint.sh
ENTRYPOINT /app/entrypoint.sh 

# Install pip dependencies and avoid
# docker layer caching invalidation
ADD ./requirements.txt /app/
RUN apk add build-base dcron && \
    pip install --no-cache --upgrade pip setuptools && \
    pip install -r requirements.txt && \
    apk del build-base && \
    rm -rf /tmp/*

# This will setup the python script in a cron job
# /proc/1/fd/1 will output the stdout for docker
RUN echo -e "* * * * * cd /app && python -m hubs_bot.app > /dev/stdout 2>&1 \n" > ./crontab
RUN crontab ./crontab

ADD . .
