#!/bin/sh

envsubst < /usr/share/nginx/html/index.html.tmpl > /tmp/index.html

exec "$@"
