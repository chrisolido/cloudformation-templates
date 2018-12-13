#!/bin/sh
set -e

# this allows us to either provide our own ENV variables or use default value
bin/rails db:create
# allows CMD to execute
exec "$@"