# Start from an Ubuntu image
FROM ubuntu:latest

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install Python and pip
RUN apt update && \
    apt install -y python3 python3-pip python3-dev libffi-dev g++ gcc musl-dev && \
    apt install -y libpq-dev python3-setuptools python3-reportlab libfreetype-dev wget git build-base && \
    apt install -y python3 py3-pip wget

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
