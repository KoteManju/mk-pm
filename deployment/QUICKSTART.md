# Quick Start: Deploy Karyaradhane to FreeBSD on Google Cloud

## Overview
This guide will help you deploy **Karyaradhane** (your project management application) to a FreeBSD server on Google Cloud Platform in about 30-60 minutes.

## What You'll Deploy
- **Backend API** (FastAPI + PostgreSQL) on FreeBSD server
- **Desktop Application** remains on users' Windows machines, connects to the hosted API

---

## Step-by-Step Deployment

### 1. Create GCP FreeBSD Instance (5-10 minutes)

**Option A: Using gcloud CLI** (recommended)
```bash
gcloud compute instances create karyaradhane-server \
    --image-family=freebsd-13-2 \
    --image-project=freebsd-org-cloud-dev \
    --machine-type=e2-medium \
    --boot-disk-size=20GB \
    --zone=us-central1-a \
    --tags=http-server,https-server

# Allow API port
gcloud compute firewall-rules create allow-api \
    --allow tcp:8000 \
    --target-tags http-server
```

**Option B: Using GCP Console**
1. Go to Compute Engine → VM Instances → Create Instance
2. Select FreeBSD 13.2 as the OS
3. Choose e2-medium (2 vCPU, 4GB RAM)
4. Enable HTTP/HTTPS traffic
5. Click Create

**Note your external IP address!**

### 2. Connect to Server (1 minute)
```bash
gcloud compute ssh karyaradhane-server --zone=us-central1-a
```

### 3. Install Dependencies (10-15 minutes)
```bash
# Update system
sudo pkg update && sudo pkg upgrade -y

# Install everything needed
sudo pkg install -y python311 py311-pip postgresql15-server \
    postgresql15-client nginx supervisor git

# Enable services
sudo sysrc postgresql_enable="YES"
sudo sysrc nginx_enable="YES"
sudo sysrc supervisord_enable="YES"

# Initialize and start PostgreSQL
sudo service postgresql initdb
sudo service postgresql start
```

### 4. Setup Database (2 minutes)
```bash
# Create database
sudo su - postgres
psql -c "CREATE DATABASE karyaradhane;"
psql -c "CREATE USER karyaradhane_user WITH PASSWORD 'ChangeThisPassword123!';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE karyaradhane TO karyaradhane_user;"
psql -c "ALTER DATABASE karyaradhane OWNER TO karyaradhane_user;"
exit
```

### 5. Deploy Application (5-10 minutes)
```bash
# Create app directory
sudo mkdir -p /opt/karyaradhane
sudo chown $USER:$USER /opt/karyaradhane

# Clone repository
cd /opt/karyaradhane
git clone https://github.com/KoteManju/mk-pm.git .

# Setup Python environment
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Configure Environment (3 minutes)
```bash
# Create .env file
cat > /opt/karyaradhane/backend/.env << 'EOF'
DATABASE_URL=postgresql://karyaradhane_user:ChangeThisPassword123!@localhost/karyaradhane
SECRET_KEY=$(python3.11 -c 'import secrets; print(secrets.token_urlsafe(32))')
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF

# Initialize database with default users
cd /opt/karyaradhane/backend
source venv/bin/activate
python init_db.py
```

### 7. Setup Supervisor (3 minutes)
```bash
# Copy supervisor config
sudo mkdir -p /usr/local/etc/supervisord.d
sudo cp /opt/karyaradhane/deployment/supervisor.ini \
    /usr/local/etc/supervisord.d/karyaradhane.ini

# Start supervisor
sudo service supervisord start

# Check status
sudo supervisorctl status
```

### 8. Setup Nginx (3 minutes)
```bash
# Backup original config
sudo mv /usr/local/etc/nginx/nginx.conf /usr/local/etc/nginx/nginx.conf.bak

# Copy new config
sudo cp /opt/karyaradhane/deployment/nginx.conf /usr/local/etc/nginx/nginx.conf

# Test and start
sudo nginx -t
sudo service nginx start
```

### 9. Test Deployment (2 minutes)
```bash
# Test locally
curl http://localhost:8000/health

# Get your external IP
curl http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google"

# Test externally (from your local machine)
curl http://YOUR_EXTERNAL_IP/api/health
```

### 10. Update Desktop App Configuration (2 minutes)

On your Windows machine, update the API URL in the desktop app to point to your server:

In `desktop/src/api/client.py`, change:
```python
self.base_url = "http://YOUR_EXTERNAL_IP"
```

Or configure it to be environment-based for production builds.

---

## Verification Checklist

- [ ] Server created and running
- [ ] PostgreSQL installed and running
- [ ] Database created with user
- [ ] Application code deployed
- [ ] Python dependencies installed
- [ ] .env file configured
- [ ] Supervisor running the app
- [ ] Nginx proxying requests
- [ ] API responds at `/health` endpoint
- [ ] Desktop app connects successfully

---

## Default Credentials

After initialization, you can login with:
- **Username**: admin
- **Password**: admin123

**⚠️ IMPORTANT: Change these immediately in production!**

---

## Next Steps

### Security (Do before going to production!)
```bash
# Generate a strong SECRET_KEY
python3.11 -c 'import secrets; print(secrets.token_urlsafe(32))'
# Update this in .env file

# Change database password
sudo su - postgres
psql -c "ALTER USER karyaradhane_user WITH PASSWORD 'NewStrongPassword123!';"
exit
# Update DATABASE_URL in .env

# Restart application
sudo supervisorctl restart karyaradhane
```

### Get SSL Certificate (Optional but recommended)
```bash
sudo pkg install -y py311-certbot py311-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Setup Automated Backups
```bash
# Make backup script executable
chmod +x /opt/karyaradhane/deployment/backup.sh

# Add to crontab (daily backup at 2 AM)
crontab -e
# Add this line:
0 2 * * * /opt/karyaradhane/deployment/backup.sh
```

---

## Useful Commands

```bash
# View logs
sudo tail -f /var/log/karyaradhane.out.log
sudo tail -f /var/log/karyaradhane.err.log

# Restart application
sudo supervisorctl restart karyaradhane

# Check application status
sudo supervisorctl status

# Update application code
cd /opt/karyaradhane
git pull
source backend/venv/bin/activate
pip install -r backend/requirements.txt
sudo supervisorctl restart karyaradhane

# Manual backup
/opt/karyaradhane/deployment/backup.sh
```

---

## Troubleshooting

**Application won't start?**
```bash
sudo tail -f /var/log/karyaradhane.err.log
```

**Can't connect to database?**
```bash
psql -U karyaradhane_user -d karyaradhane -h localhost
# Check DATABASE_URL in .env matches
```

**Nginx errors?**
```bash
sudo nginx -t  # Test configuration
sudo tail -f /var/log/nginx/error.log
```

---

## Cost Estimate
- e2-medium instance: ~$25/month
- 20GB disk: ~$1/month
- **Total: ~$26/month**

---

## Support
For detailed information, see `FREEBSD_GCP_SETUP.md` in this directory.
