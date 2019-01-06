#!/bin/sh
set -e

if [ "$RAILS_ENV" != production ]; then
  bin/rails db:create
fi

bin/rails db:migrate
echo $RAILS_MASTER_KEY > config/master.key
RAILS_ENV=production bundle exec rake assets:precompile

exec "$@"
