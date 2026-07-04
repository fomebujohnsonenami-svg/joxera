#!/usr/bin/env bash
# Joxera preview bootstrap — reinstalls the system stack that the preview pod
# does NOT persist across restarts (PostgreSQL 15 + PostGIS + pgvector + Redis
# + GDAL/GEOS), recreates the DB, runs migrations, and seeds demo users.
#
# Usage:  bash /app/scripts/setup_env.sh
#
# NOTE: Production hosting should use an external platform (Railway/Render/etc.)
# with managed Postgres/Redis — this script is only for the ephemeral preview.
set -euo pipefail

echo "==> Installing system packages (apt)"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y >/tmp/setup_apt_update.log 2>&1
apt-get install -y \
  postgresql-15 postgresql-contrib postgresql-15-postgis-3 postgresql-server-dev-15 \
  redis-server gdal-bin libgdal-dev libgeos-dev binutils libproj-dev build-essential git \
  >/tmp/setup_apt_install.log 2>&1

echo "==> Building pgvector 0.8.0 from source"
if [ ! -f /usr/lib/postgresql/15/lib/vector.so ]; then
  cd /tmp && rm -rf pgvector
  git clone --depth 1 --branch v0.8.0 https://github.com/pgvector/pgvector.git >/tmp/setup_pgvector.log 2>&1
  cd pgvector && make >>/tmp/setup_pgvector.log 2>&1 && make install >>/tmp/setup_pgvector.log 2>&1
fi

echo "==> Starting PostgreSQL + Redis"
service postgresql start || pg_ctlcluster 15 main start
service redis-server start
sleep 3

echo "==> Creating database, role and extensions (idempotent)"
sudo -u postgres psql <<'SQL'
DO $$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'joxera') THEN
    CREATE USER joxera WITH PASSWORD 'joxera' SUPERUSER;
  END IF;
END $$;
SELECT 'CREATE DATABASE joxera OWNER joxera'
  WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'joxera')\gexec
SQL
sudo -u postgres psql -d joxera <<'SQL'
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;
SQL

echo "==> Running Django migrations"
cd /app/backend
set -a; . ./.env; set +a
/root/.venv/bin/python manage.py migrate --noinput

echo "==> Seeding demo users"
/root/.venv/bin/python manage.py shell <<'PY'
from users.models import User, KYCStatus, UserRole
for handle, email, role in [
    ("talentdemo", "talent.demo@joxera.test", UserRole.TALENT),
    ("employerdemo", "employer.demo@joxera.test", UserRole.EMPLOYER),
]:
    u, _ = User.objects.get_or_create(email=email, defaults=dict(
        username=handle, handle=handle, role=role, country_code="US"))
    u.set_password("DemoPass123!")
    u.kyc_status = KYCStatus.APPROVED
    u.verified_badge = True
    u.save()
print("seeded demo users")
PY

echo "==> Restarting backend"
sudo supervisorctl restart backend
echo "==> Done. Health:"; sleep 5; curl -s http://localhost:8001/api/health/ || true
