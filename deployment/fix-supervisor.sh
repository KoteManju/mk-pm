#!/bin/sh
# Repair supervisor so karyaradhane program loads and starts

set -e

APP_DIR="/opt/karyaradhane"

info() { printf ">> %s\n" "$1"; }

info "Installing supervisord main config..."
sudo mkdir -p /var/run /usr/local/etc/supervisord.d
sudo cp "$APP_DIR/deployment/supervisord.conf" /usr/local/etc/supervisord.conf
sudo cp "$APP_DIR/deployment/supervisor.ini" /usr/local/etc/supervisord.d/karyaradhane.ini
sudo touch /var/log/supervisord.log /var/log/karyaradhane.out.log /var/log/karyaradhane.err.log
sudo chown www:www /var/log/karyaradhane.out.log /var/log/karyaradhane.err.log 2>/dev/null || true

info "Restarting supervisord..."
sudo service supervisord restart 2>/dev/null || sudo service supervisord start
sleep 2

info "Supervisor status:"
sudo supervisorctl -c /usr/local/etc/supervisord.conf status || true
sudo supervisorctl -c /usr/local/etc/supervisord.conf avail || true

info "Starting karyaradhane..."
sudo supervisorctl -c /usr/local/etc/supervisord.conf reread
sudo supervisorctl -c /usr/local/etc/supervisord.conf update
sudo supervisorctl -c /usr/local/etc/supervisord.conf start karyaradhane || \
    sudo supervisorctl -c /usr/local/etc/supervisord.conf restart karyaradhane

sleep 2
sudo supervisorctl -c /usr/local/etc/supervisord.conf status

info "If RUNNING, test with: curl http://127.0.0.1:8000/health"
