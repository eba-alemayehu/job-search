FROM nginx:1.23.2-alpine as base-build

RUN apk update
RUN apk add python3-dev wget git nodejs npm build-base

FROM base-build AS nginx-config-build
COPY ./default.conf /etc/nginx/conf.d/default.conf

