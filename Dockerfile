FROM python:3-alpine as hubs_bot
MAINTAINER m@rkis.cc
WORKDIR /app

# crond doesn't like being launched directly
# this will use a shell script to launch it
RUN echo -e "rm -rf /var/spool/cron/crontabs && mkdir -m 0644 -p /var/spool/cron/crontabs \n" > ./entrypoint.sh
RUN echo -e "chmod -R 0644 /var/spool/cron/crontabs \n" > ./entrypoint.sh
RUN echo -e "mkdir -p /var/log/cron && touch /var/log/cron/cron.log && chmod 0666 /var/log/cron/cron.log \n" > .entrypoint.sh
RUN echo -e "crond -s /var/spool/cron/crontabs -b -L /var/log/cron/cron.log \n" > ./entrypoint.sh
RUN chmod +x ./entrypoint.sh
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
