#!/bin/sh
# Initialize PostgreSQL 18 on FreeBSD when data18 is missing

set -e

info() { printf ">> %s\n" "$1"; }

info "Configuring PostgreSQL 18..."
sudo pkg install -y postgresql18-server postgresql18-client
sudo sysrc postgresql_enable="YES"
sudo sysrc postgresql_data="/var/db/postgres/data18"

if [ ! -d /var/db/postgres/data18 ]; then
    info "Creating new PostgreSQL 18 cluster in data18..."
    sudo service postgresql initdb
fi

info "Starting PostgreSQL..."
sudo service postgresql stop 2>/dev/null || true
for PGDATA in /var/db/postgres/data15 /var/db/postgres/data18; do
    if [ -f "$PGDATA/postmaster.pid" ]; then
        sudo -u postgres /usr/local/bin/pg_ctl -D "$PGDATA" stop -m fast 2>/dev/null || true
    fi
done
sleep 2
sudo mkdir -p /var/db/postgres/data18/log
sudo chown -R postgres:postgres /var/db/postgres/data18
if ! sudo service postgresql start; then
    sudo -u postgres /usr/local/bin/pg_ctl -D /var/db/postgres/data18 -l /var/db/postgres/data18/log/postgresql.log start
fi

info "Creating app database and user..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = 'karyaradhane'" | grep -q 1 \
    || sudo -u postgres psql -c "CREATE DATABASE karyaradhane;"
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname = 'karyaradhane_user'" | grep -q 1 \
    || sudo -u postgres psql -c "CREATE USER karyaradhane_user WITH PASSWORD 'ChangeThisPassword123!';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE karyaradhane TO karyaradhane_user;" || true
sudo -u postgres psql -c "ALTER DATABASE karyaradhane OWNER TO karyaradhane_user;" || true

info "PostgreSQL 18 ready. Continue with:"
echo "  cd /opt/karyaradhane && sh deployment/freebsd-setup.sh"
