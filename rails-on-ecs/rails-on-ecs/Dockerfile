FROM ruby:2.5-alpine

RUN apk update && apk add libpq

RUN apk add --no-cache --update \
        build-base linux-headers git tzdata \
        postgresql-dev yarn nodejs \
    && rm -rf /var/cache/apk/*

WORKDIR /usr/src/app

COPY Gemfile .
COPY Gemfile.lock .

RUN bundle install --deployment

COPY . .
RUN chmod +x /usr/src/app/docker-entrypoint.sh

EXPOSE 3000

ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]

CMD bundle exec rails server -p 3000 -b '0.0.0.0'
