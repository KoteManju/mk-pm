#!/bin/sh
# First-time FreeBSD server setup for mk-pm (Karyaradhane)
# Run on the GCP FreeBSD VM after SSH login (not as root).

set -e

APP_DIR="/opt/karyaradhane"
BACKEND_DIR="$APP_DIR/backend"
VENV_DIR="$BACKEND_DIR/venv"
REPO_URL="https://github.com/KoteManju/mk-pm.git"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info() { printf "${GREEN}✓${NC} %s\n" "$1"; }
warn() { printf "${YELLOW}⚠${NC} %s\n" "$1"; }
fail() { printf "${RED}✗${NC} %s\n" "$1"; exit 1; }

if [ "$(id -u)" = "0" ]; then
    fail "Run as your normal user (with sudo), not root."
fi

info "Installing system packages (FreeBSD $(freebsd-version -u))..."
sudo pkg update

# Install PostgreSQL server FIRST (FreeBSD 15 uses PG 18; avoids pkg removing server)
info "Installing PostgreSQL 18 server..."
sudo pkg remove -y postgresql15-server postgresql15-client 2>/dev/null || true
sudo pkg install -y postgresql18-server postgresql18-client

info "Installing application packages..."
sudo pkg install -y python311 py311-pip py311-psycopg2 nginx py311-supervisor git curl

info "Enabling services..."
sudo sysrc postgresql_enable="YES"
sudo sysrc postgresql_data="/var/db/postgres/data18"
sudo sysrc nginx_enable="YES"
sudo sysrc supervisord_enable="YES"

# Initialize PostgreSQL 18 cluster if missing
if [ ! -d /var/db/postgres/data18 ]; then
    info "Initializing PostgreSQL 18 cluster (data18)..."
    sudo service postgresql initdb
fi

info "Starting PostgreSQL..."
if ! sudo service postgresql start; then
    warn "PostgreSQL failed to start. Check: sudo tail /var/db/postgres/data18/log/*.log"
    fail "Fix PostgreSQL before continuing."
fi

info "Preparing application directory..."
sudo mkdir -p "$APP_DIR"
sudo chown "$USER":"$USER" "$APP_DIR"

if [ -d "$APP_DIR/.git" ]; then
    cd "$APP_DIR"
    git pull origin main
else
    git clone "$REPO_URL" "$APP_DIR"
fi

cd "$BACKEND_DIR"

if [ ! -d "$VENV_DIR" ]; then
    info "Creating Python virtual environment..."
    python3.11 -m venv venv
fi

. "$VENV_DIR/bin/activate"
pip install --upgrade pip
info "Installing Python dependencies (FreeBSD requirements)..."
if ! pip install -r "$APP_DIR/deployment/requirements-freebsd.txt"; then
    warn "Pip install failed; installing Rust compiler and retrying..."
    sudo pkg install -y rust
    pip install -r "$APP_DIR/deployment/requirements-freebsd.txt"
fi

if [ ! -f "$BACKEND_DIR/.env" ]; then
    warn "Creating .env from deployment template - edit passwords before production use."
    cp "$APP_DIR/deployment/.env.example" "$BACKEND_DIR/.env"
    SECRET=$(python3.11 -c 'import secrets; print(secrets.token_urlsafe(32))')
    sed -i '' "s|your_secret_key_here_generate_with_openssl_rand_base64_32|$SECRET|" "$BACKEND_DIR/.env" 2>/dev/null \
        || sed -i "s|your_secret_key_here_generate_with_openssl_rand_base64_32|$SECRET|" "$BACKEND_DIR/.env"
fi

info "Setting up PostgreSQL database (if not exists)..."
DB_PASS=$(grep DATABASE_URL "$BACKEND_DIR/.env" | sed 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/')
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = 'karyaradhane'" | grep -q 1 \
    || sudo -u postgres psql -c "CREATE DATABASE karyaradhane;"
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname = 'karyaradhane_user'" | grep -q 1 \
    || sudo -u postgres psql -c "CREATE USER karyaradhane_user WITH PASSWORD '${DB_PASS:-ChangeThisPassword123!}';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE karyaradhane TO karyaradhane_user;" || true
sudo -u postgres psql -c "ALTER DATABASE karyaradhane OWNER TO karyaradhane_user;" || true

export PYTHONPATH="$BACKEND_DIR"
info "Initializing database schema and sample data..."
python init_db.py
python migrate_chat_features.py || true
python migrate_email_features.py || true
python migrate_attachments.py || true

info "Creating upload directory..."
mkdir -p "$BACKEND_DIR/uploads"
sudo chown -R www:www "$BACKEND_DIR/uploads" 2>/dev/null || sudo chown -R www "$BACKEND_DIR/uploads"

info "Installing supervisor and nginx configs..."
sudo mkdir -p /usr/local/etc/supervisord.d
sudo cp "$APP_DIR/deployment/supervisor.ini" /usr/local/etc/supervisord.d/karyaradhane.ini
sudo cp "$APP_DIR/deployment/nginx.conf" /usr/local/etc/nginx/nginx.conf
sudo mkdir -p /var/log/nginx
sudo touch /var/log/karyaradhane.out.log /var/log/karyaradhane.err.log
sudo chown www:www /var/log/karyaradhane.out.log /var/log/karyaradhane.err.log 2>/dev/null \
    || sudo chown www /var/log/karyaradhane.out.log /var/log/karyaradhane.err.log

sudo service supervisord start 2>/dev/null || sudo service supervisord restart
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart karyaradhane || sudo supervisorctl start karyaradhane

sudo nginx -t
sudo service nginx restart

info "Running verification checks..."
sleep 3
sh "$APP_DIR/deployment/verify-deployment.sh"

info "Setup complete."
echo ""
echo "External URL: http://YOUR_VM_EXTERNAL_IP/health"
echo "API docs:     http://YOUR_VM_EXTERNAL_IP/docs"
echo "Desktop app:  Settings -> API URL -> http://YOUR_VM_EXTERNAL_IP"
echo "Login:        admin / admin123"
