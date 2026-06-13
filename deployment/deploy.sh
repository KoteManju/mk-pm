#!/bin/sh
# Update mk-pm on an existing FreeBSD deployment

set -e

APP_DIR="/opt/karyaradhane"
BACKEND_DIR="$APP_DIR/backend"
VENV_DIR="$BACKEND_DIR/venv"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { printf "${GREEN}✓${NC} %s\n" "$1"; }
print_error() { printf "${RED}✗${NC} %s\n" "$1"; }
print_warning() { printf "${YELLOW}⚠${NC} %s\n" "$1"; }

if [ "$(id -u)" = "0" ]; then
    print_error "Do not run as root."
    exit 1
fi

cd "$APP_DIR"
print_status "Pulling latest code..."
git pull origin main

cd "$BACKEND_DIR"
. "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

export PYTHONPATH="$BACKEND_DIR"
print_status "Running database migrations..."
python migrate_chat_features.py || true
python migrate_email_features.py || true
python migrate_attachments.py || true

mkdir -p "$BACKEND_DIR/uploads"

if command -v supervisorctl > /dev/null; then
    print_status "Restarting application..."
    sudo supervisorctl restart karyaradhane
    sleep 3
    sudo supervisorctl status karyaradhane
else
    print_warning "Supervisor not found."
fi

print_status "Verifying deployment..."
sh "$APP_DIR/deployment/verify-deployment.sh"

print_status "Deployment update completed."
