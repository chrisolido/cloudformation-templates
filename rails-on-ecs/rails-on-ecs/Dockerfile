FROM ruby:2.5-alpine

RUN apk update && apk add libpq tzdata yarn nodejs 
WORKDIR /usr/src/app

COPY Gemfile .
COPY Gemfile.lock .

RUN apk add --no-cache --virtual .build-deps \
        build-base linux-headers git postgresql-dev \
    && bundle install --deployment \
    && apk del .build-deps

COPY . .
RUN chmod +x /usr/src/app/docker-entrypoint.sh

EXPOSE 3000

ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]

CMD bundle exec puma -C config/puma.rb -b tcp://0.0.0.0:3000
