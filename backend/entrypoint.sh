#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! python -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1)
try:
    s.connect(('${POSTGRES_HOST:-db}', int('${POSTGRES_PORT:-5432}')))
    s.close()
    exit(0)
except OSError:
    exit(1)
" 2>/dev/null; do
  sleep 1
done
echo "PostgreSQL is ready."

python manage.py migrate --noinput
python manage.py collectstatic --noinput 2>/dev/null || true

exec "$@"
