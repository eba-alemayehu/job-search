FROM python:3.10-alpine as base-builder

RUN apk update
RUN apk add python3-dev libffi-dev g++ gcc musl-dev python3-dev  \
    libpq-dev py3-setuptools py3-reportlab freetype-dev wget git build-base \
    python3 py3-pip wget
RUN pip install --upgrade pip

FROM base-builder as python-builder
COPY ./requirement.txt .
RUN pip install -r requirement.txt  --no-build-isolation

FROM python-builder as app-builder
COPY . /app
WORKDIR /app

FROM app-builder as app-start-builder
COPY ./setup.sh /
ENV DEBUG false

RUN printenv

CMD ["sh", "/setup.sh"]
RUN echo "Done!"
