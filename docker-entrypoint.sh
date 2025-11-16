#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! pg_isready -h ${DB_HOST:-postgres} -p ${DB_PORT:-5432} -U ${DB_USER:-govplan}; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! redis-cli -h ${REDIS_HOST:-redis} -p ${REDIS_PORT:-6379} ping; do
  sleep 1
done
echo "Redis is ready!"

# Run database initialization if needed
if [ "$RUN_MIGRATIONS" = "true" ]; then
  echo "Running database migrations..."
  python scripts/init_db.py
fi

# Execute the main command
exec "$@"
