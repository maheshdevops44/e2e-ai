#!/bin/sh

set -e

if [ -n "${DB_USERNAME:-}" ] && [ -n "${DB_PASSWORD:-}" ] && \
   [ -n "${DB_HOST:-}" ] && [ -n "${DB_PORT:-}" ] && [ -n "${DB_DATABASE:-}" ]; then
  echo "DEBUG: DB_HOST=${DB_HOST}"
  echo "DEBUG: DB_PORT=${DB_PORT}"
  echo "DEBUG: DB_DATABASE=${DB_DATABASE}"
  echo "DEBUG: DB_USERNAME=${DB_USERNAME}"

  # Validate that DB_PORT is a valid number
  if ! echo "$DB_PORT" | grep -q '^[0-9]\+$'; then
    echo "ERROR: DB_PORT '${DB_PORT}' is not a valid number" >&2
    exit 1
  fi

  export DATABASE_URL="postgresql://${DB_USERNAME}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_DATABASE}"
fi

if [ -z "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL is not set" >&2
  exit 1
fi

echo "Running Prisma migrations"
prisma migrate deploy

echo "Starting the application"
exec node server.js

echo "Started service"