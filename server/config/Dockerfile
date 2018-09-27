FROM python:3.6

RUN apt-get update && apt-get install -y cron
RUN pip3 install pipenv

COPY Pipfile* /secret-club/
WORKDIR /secret-club/
RUN pipenv install --system
RUN rm Pipfile*

ADD config/crontab /etc/cron.d/secretclub-cron
RUN chmod 0644 /etc/cron.d/secretclub-cron
RUN crontab /etc/cron.d/secretclub-cron

COPY src src/
RUN touch runs.log
