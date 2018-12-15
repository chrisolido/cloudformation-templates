#!/bin/sh
set -e

PLACEHOLDER_BACKEND_NAME=${BACKEND_NAME:=localhost}
PLACEHOLDER_BACKEND_PORT=${BACKEND_PORT:=3000}
PLACEHOLDER_HOST=${HOST_URL:=localhost}

DEFAULT_CONFIG_PATH="/etc/nginx/conf.d/default.conf"

# Replace all instances of the placeholders with the values above.
sed -i "s/PLACEHOLDER_HOST/${PLACEHOLDER_HOST}/g" "${DEFAULT_CONFIG_PATH}"
sed -i "s/PLACEHOLDER_BACKEND_NAME/${PLACEHOLDER_BACKEND_NAME}/g" "${DEFAULT_CONFIG_PATH}"
sed -i "s/PLACEHOLDER_BACKEND_PORT/${PLACEHOLDER_BACKEND_PORT}/g" "${DEFAULT_CONFIG_PATH}"

exec "$@"
