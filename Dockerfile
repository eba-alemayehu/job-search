FROM python:3.10-alpine as base-builder

RUN apk update
RUN apk add python3-dev libffi-dev g++ gcc musl-dev \
    libpq-dev py3-setuptools py3-reportlab freetype-dev wget git build-base \
    python3 py3-pip wget
RUN pip install --upgrade pip

WORKDIR /a
COPY ./requirement.txt .
COPY cronfile /etc/cron.d/mycron
COPY cronjob.sh /cronjob.sh

RUN chmod +x /cronjob.sh
RUN crontab /etc/cron.d/mycron
RUN touch /var/log/cron.log

RUN pip install -r requirement.txt  --no-build-isolation
COPY . .
CMD ["sh", "./setup.sh"]
RUN echo "Done!"
