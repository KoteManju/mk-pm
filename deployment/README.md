# Karyaradhane Deployment Files

This directory contains deployment configurations for hosting Karyaradhane on FreeBSD in Google Cloud Platform.

## Files Overview

- **FREEBSD_GCP_SETUP.md** - Complete step-by-step guide for deploying on FreeBSD/GCP
- **nginx.conf** - Nginx reverse proxy configuration
- **supervisor.ini** - Supervisor process manager configuration
- **deploy.sh** - Automated deployment script
- **backup.sh** - Database backup script
- **.env.example** - Example environment variables file
- **requirements-prod.txt** - Production Python dependencies

## Quick Start

1. Follow the instructions in `FREEBSD_GCP_SETUP.md`
2. Copy and configure the files to your FreeBSD server
3. Run `deploy.sh` to automate the deployment
4. Set up a cron job for `backup.sh` to run daily

## Architecture

```
┌─────────────────┐
│  Desktop App    │ (Windows .exe)
│  (PySide6)      │
└────────┬────────┘
         │
         │ HTTPS
         ▼
┌─────────────────────────────────┐
│   FreeBSD Server (GCP)          │
│                                 │
│  ┌──────────┐    ┌──────────┐  │
│  │  Nginx   │───▶│ FastAPI  │  │
│  │  (80/443)│    │ (8000)   │  │
│  └──────────┘    └─────┬────┘  │
│                        │        │
│                        ▼        │
│                  ┌──────────┐  │
│                  │PostgreSQL│  │
│                  └──────────┘  │
└─────────────────────────────────┘
```

## Security Checklist

- [ ] Changed default PostgreSQL password
- [ ] Generated secure SECRET_KEY
- [ ] Configured firewall rules
- [ ] Enabled SSL/TLS with Let's Encrypt
- [ ] Set up automated backups
- [ ] Configured log rotation
- [ ] Enabled fail2ban (optional)
- [ ] Set up monitoring/alerts

## Maintenance

### View Application Logs
```bash
sudo tail -f /var/log/karyaradhane.out.log
sudo tail -f /var/log/karyaradhane.err.log
```

### Restart Application
```bash
sudo supervisorctl restart karyaradhane
```

### Update Application
```bash
cd /opt/karyaradhane
./deployment/deploy.sh
```

### Manual Backup
```bash
./deployment/backup.sh
```

## Support

For issues or questions, refer to the main project documentation or open an issue on GitHub.
