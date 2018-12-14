FROM ruby:2.5-alpine

RUN apk update && apk add libpq

WORKDIR /usr/src/app

COPY Gemfile .
COPY Gemfile.lock .

RUN apk add --no-cache --update \
        build-base linux-headers git tzdata \
        postgresql-dev sqlite sqlite-dev nodejs \
    && rm -rf /var/cache/apk/*

RUN bundle install --deployment

COPY . .
COPY db-migrations.sh /db-migrations.sh
RUN chmod +x /db-migrations.sh

EXPOSE 3000