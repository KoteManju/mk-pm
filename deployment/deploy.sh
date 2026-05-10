#!/bin/sh
# Karyaradhane Deployment Script for FreeBSD

set -e

echo "🚀 Starting Karyaradhane deployment..."

# Configuration
APP_DIR="/opt/karyaradhane"
BACKEND_DIR="$APP_DIR/backend"
VENV_DIR="$BACKEND_DIR/venv"
REPO_URL="https://github.com/KoteManju/mk-pm.git"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo "${GREEN}✓${NC} $1"
}

print_error() {
    echo "${RED}✗${NC} $1"
}

print_warning() {
    echo "${YELLOW}⚠${NC} $1"
}

# Check if running as root
if [ "$(id -u)" = "0" ]; then
    print_error "Do not run this script as root. Run as regular user with sudo access."
    exit 1
fi

# Create application directory if it doesn't exist
if [ ! -d "$APP_DIR" ]; then
    print_status "Creating application directory..."
    sudo mkdir -p "$APP_DIR"
    sudo chown $USER:$USER "$APP_DIR"
fi

cd "$APP_DIR"

# Clone or update repository
if [ -d ".git" ]; then
    print_status "Updating repository..."
    git pull origin main
else
    print_status "Cloning repository..."
    git clone "$REPO_URL" .
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    print_status "Creating virtual environment..."
    cd "$BACKEND_DIR"
    python3.11 -m venv venv
fi

# Activate virtual environment and install dependencies
print_status "Installing Python dependencies..."
cd "$BACKEND_DIR"
. "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env exists
if [ ! -f "$BACKEND_DIR/.env" ]; then
    print_warning ".env file not found. Please create it manually."
    echo "Example .env file:"
    echo "DATABASE_URL=postgresql://user:password@localhost/karyaradhane"
    echo "SECRET_KEY=your_secret_key_here"
    echo "ALGORITHM=HS256"
    echo "ACCESS_TOKEN_EXPIRE_MINUTES=30"
else
    print_status ".env file found"
fi

# Run database migrations (if using Alembic)
# print_status "Running database migrations..."
# alembic upgrade head

# Restart application via supervisor
if command -v supervisorctl > /dev/null; then
    print_status "Restarting application..."
    sudo supervisorctl restart karyaradhane
    sleep 2
    sudo supervisorctl status karyaradhane
else
    print_warning "Supervisor not found. Please restart the application manually."
fi

# Test API health
print_status "Testing API endpoint..."
sleep 3
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "API is responding correctly!"
else
    print_error "API health check failed. Check logs with: sudo tail -f /var/log/karyaradhane.err.log"
fi

print_status "Deployment completed successfully! 🎉"
echo ""
echo "Useful commands:"
echo "  View logs: sudo tail -f /var/log/karyaradhane.out.log"
echo "  Restart app: sudo supervisorctl restart karyaradhane"
echo "  Check status: sudo supervisorctl status"
