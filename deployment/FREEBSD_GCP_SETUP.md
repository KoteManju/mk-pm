# Karyaradhane - FreeBSD Deployment on Google Cloud Platform

## Prerequisites
- Google Cloud Platform account
- gcloud CLI installed on your local machine
- SSH key pair for authentication

## Step 1: Create FreeBSD Instance on GCP

### Using gcloud CLI:
```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Create a FreeBSD 13.x instance
gcloud compute instances create karyaradhane-server \
    --image-family=freebsd-13-2 \
    --image-project=freebsd-org-cloud-dev \
    --machine-type=e2-medium \
    --boot-disk-size=20GB \
    --boot-disk-type=pd-standard \
    --zone=us-central1-a \
    --tags=http-server,https-server

# Create firewall rules
gcloud compute firewall-rules create allow-http \
    --allow tcp:80 \
    --target-tags http-server \
    --description="Allow HTTP traffic"

gcloud compute firewall-rules create allow-https \
    --allow tcp:443 \
    --target-tags https-server \
    --description="Allow HTTPS traffic"

gcloud compute firewall-rules create allow-api \
    --allow tcp:8000 \
    --target-tags http-server \
    --description="Allow API traffic"
```

### Using GCP Console:
1. Go to **Compute Engine** > **VM Instances**
2. Click **Create Instance**
3. Configure:
   - **Name**: karyaradhane-server
   - **Region**: us-central1 (or your preferred region)
   - **Machine type**: e2-medium (2 vCPU, 4 GB memory)
   - **Boot disk**: 
     - Click "Change"
     - Select "Public images"
     - Select "FreeBSD" from OS dropdown
     - Select "freebsd-13-2" version
     - Disk size: 20 GB
   - **Firewall**: Allow HTTP and HTTPS traffic
4. Click **Create**

## Step 2: Connect to Your FreeBSD Instance

```bash
# SSH into the instance
gcloud compute ssh karyaradhane-server --zone=us-central1-a
```

## Step 3: Initial FreeBSD Setup

```bash
# Update package repository
sudo pkg update
sudo pkg upgrade -y

# Install required packages
sudo pkg install -y python311 py311-pip postgresql15-server postgresql15-client \
    nginx supervisor git curl wget

# Enable services
sudo sysrc postgresql_enable="YES"
sudo sysrc nginx_enable="YES"
sudo sysrc supervisord_enable="YES"

# Initialize PostgreSQL
sudo service postgresql initdb

# Start PostgreSQL
sudo service postgresql start
```

## Step 4: Configure PostgreSQL

```bash
# Switch to postgres user
sudo su - postgres

# Create database and user
psql -c "CREATE DATABASE karyaradhane;"
psql -c "CREATE USER karyaradhane_user WITH PASSWORD 'your_secure_password_here';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE karyaradhane TO karyaradhane_user;"
psql -c "ALTER DATABASE karyaradhane OWNER TO karyaradhane_user;"

# Exit postgres user
exit
```

## Step 5: Deploy Application

```bash
# Create application directory
sudo mkdir -p /opt/karyaradhane
sudo chown $USER:$USER /opt/karyaradhane
cd /opt/karyaradhane

# Clone your repository
git clone https://github.com/KoteManju/mk-pm.git .

# Create virtual environment
cd backend
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=postgresql://karyaradhane_user:your_secure_password_here@localhost/karyaradhane
SECRET_KEY=$(python3.11 -c 'import secrets; print(secrets.token_urlsafe(32))')
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF

# Run database migrations
# (Add Alembic migrations if needed)
```

## Step 6: Configure Supervisor

```bash
# Create supervisor config
sudo tee /usr/local/etc/supervisord.d/karyaradhane.ini << 'EOF'
[program:karyaradhane]
command=/opt/karyaradhane/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
directory=/opt/karyaradhane/backend
user=www
autostart=true
autorestart=true
stderr_logfile=/var/log/karyaradhane.err.log
stdout_logfile=/var/log/karyaradhane.out.log
environment=PYTHONPATH="/opt/karyaradhane/backend"
EOF

# Start supervisor
sudo service supervisord start

# Check status
sudo supervisorctl status
```

## Step 7: Configure Nginx

See `nginx.conf` file in this directory.

```bash
# Copy nginx configuration
sudo cp /opt/karyaradhane/deployment/nginx.conf /usr/local/etc/nginx/nginx.conf

# Test nginx configuration
sudo nginx -t

# Start nginx
sudo service nginx start
```

## Step 8: Verify Deployment

```bash
# Check if API is running
curl http://localhost:8000/health

# Check via external IP
curl http://YOUR_EXTERNAL_IP/api/health
```

## Step 9: SSL Certificate (Optional but Recommended)

```bash
# Install certbot
sudo pkg install -y py311-certbot py311-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
```

## Maintenance Commands

```bash
# Restart application
sudo supervisorctl restart karyaradhane

# View logs
sudo tail -f /var/log/karyaradhane.out.log
sudo tail -f /var/log/karyaradhane.err.log

# Update application
cd /opt/karyaradhane
git pull
source backend/venv/bin/activate
pip install -r backend/requirements.txt
sudo supervisorctl restart karyaradhane

# Backup database
pg_dump -U karyaradhane_user karyaradhane > backup_$(date +%Y%m%d).sql
```

## Desktop Application Distribution

The desktop application (built with PySide6) is packaged as a Windows executable and distributed separately to end users. Users download and run the .exe file on their Windows machines, which connects to the API hosted on this FreeBSD server.

## Cost Estimation

- **e2-medium instance**: ~$25/month
- **20 GB standard persistent disk**: ~$0.80/month
- **Network egress**: Variable based on usage
- **Total**: ~$26-30/month

## Security Recommendations

1. Use strong passwords for PostgreSQL
2. Enable SSL/TLS with Let's Encrypt
3. Configure firewall to only allow necessary ports
4. Regularly update packages: `sudo pkg update && sudo pkg upgrade`
5. Set up automated backups
6. Use environment variables for secrets (never commit .env)
7. Consider using GCP Secret Manager for sensitive data
