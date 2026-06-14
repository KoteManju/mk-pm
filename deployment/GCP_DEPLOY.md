# Deploy mk-pm to FreeBSD on Google Cloud

## Supported FreeBSD versions

| Version | GCP image family (recommended) | Notes |
|---------|-------------------------------|--------|
| **FreeBSD 15.0-RELEASE** | `freebsd-15-0-amd64-ufs` | Best choice for new deployments |
| **FreeBSD 15.0-STABLE** | List images in GCP* | Rolling STABLE snapshots; same setup script |
| FreeBSD 14.x | `freebsd-14-3` | Also supported |
| FreeBSD 13.x | `freebsd-13-2` | Legacy; still works |

\*Do **not** use the deprecated family `freebsd-15-0` (no architecture/filesystem suffix).  
List current images:

```bash
gcloud compute images list --project freebsd-org-cloud-dev --no-standard-images | grep 15
```

For **15.0-STABLE**, pick the latest matching family (e.g. `freebsd-15-0-stable-amd64-ufs` if listed).  
The mk-pm app runs the same on RELEASE and STABLE — only the VM image differs.

## What gets deployed

| Component | Where it runs |
|-----------|----------------|
| **Backend API** (FastAPI) | FreeBSD VM on GCP |
| **PostgreSQL** | Same VM |
| **Nginx** | Reverse proxy on port 80 |
| **Desktop app** | Your Windows PC — points to the VM URL in Settings |

The desktop app is **not** installed on the server. Users run it locally and set **Settings → API URL** to `http://YOUR_VM_IP`.

---

## Local verification (already tested on your PC)

Your local backend passed all checks:

- Health: `attachments_enabled: true`, version `1.1.0`
- Login: `admin` / `admin123`
- Projects and tasks API working

---

## Step 1: Create FreeBSD VM in GCP Console

1. Open [Google Cloud Console → Compute Engine → VM instances](https://console.cloud.google.com/compute/instances)
2. Click **Create instance**
3. Settings:
   - **Name:** `mk-pm-server`
   - **Region:** e.g. `us-central1`
   - **Machine type:** `e2-medium` (2 vCPU, 4 GB)
   - **Boot disk → Change:**
     - Public images → **FreeBSD**
     - Version: **FreeBSD 15.0** (`freebsd-15-0-amd64-ufs`) — or **15.0-STABLE** if listed
     - Filesystem: **UFS** (recommended) or ZFS (`freebsd-15-0-amd64-zfs`)
     - Size: **30 GB** minimum (FreeBSD 15 image requires at least 22 GB)
   - **Firewall:** check **Allow HTTP traffic** and **Allow HTTPS traffic**
4. Click **Create**
5. Copy the **External IP** (e.g. `34.xxx.xxx.xxx`)

### Optional: install gcloud on Windows

Download: https://cloud.google.com/sdk/docs/install

Then create the VM from PowerShell:

```powershell
gcloud config set project YOUR_PROJECT_ID

# FreeBSD 15.0 RELEASE (recommended)
gcloud compute instances create mk-pm-server `
  --image-family=freebsd-15-0-amd64-ufs `
  --image-project=freebsd-org-cloud-dev `
  --machine-type=e2-medium `
  --boot-disk-size=30GB `
  --zone=us-central1-a `
  --tags=http-server,https-server

# FreeBSD 15.0-STABLE (optional — list families first)
# gcloud compute images list --project freebsd-org-cloud-dev --no-standard-images | grep -i stable
# gcloud compute instances create mk-pm-server `
#   --image-family=freebsd-15-0-stable-amd64-ufs `
#   --image-project=freebsd-org-cloud-dev `
#   ...
```

---

## Step 2: SSH into the VM

**GCP Console:** VM instances → click **SSH** next to your VM.

**Or with gcloud:**

```bash
gcloud compute ssh mk-pm-server --zone=us-central1-a
```

---

## Step 3: Run one-command setup on the VM

```bash
fetch -o - https://raw.githubusercontent.com/KoteManju/mk-pm/main/deployment/freebsd-setup.sh | sh
```

If `fetch` fails, clone first:

```bash
sudo pkg install -y git
git clone https://github.com/KoteManju/mk-pm.git /opt/karyaradhane
sh /opt/karyaradhane/deployment/freebsd-setup.sh
```

The script installs Python, PostgreSQL, Nginx, Supervisor, clones the repo, initializes the DB, and starts the API.

---

## Step 4: Verify on the server

```bash
# On the VM
sh /opt/karyaradhane/deployment/verify-deployment.sh

# Through nginx (replace with your external IP)
curl http://YOUR_EXTERNAL_IP/health
curl http://YOUR_EXTERNAL_IP/docs
```

Expected health response:

```json
{"status":"healthy","email_enabled":false,"attachments_enabled":true,"version":"1.1.0"}
```

---

## Step 5: Connect the desktop app

1. Run `start_backend.bat` is **not** needed for cloud — only the desktop app locally.
2. Start **`start_desktop.bat`**
3. Go to **Settings**
4. Set **API URL** to: `http://YOUR_EXTERNAL_IP` (no trailing slash)
5. Click **Test connection** / save
6. Log in with **admin** / **admin123**

---

## Firewall note

Port **80** is open if you enabled HTTP traffic. The API also listens on **8000** internally (nginx proxies to it). You do **not** need to expose 8000 publicly if nginx is working.

---

## Update after code changes

On the VM:

```bash
sh /opt/karyaradhane/deployment/deploy.sh
```

---

## Troubleshooting

```bash
sudo supervisorctl status
sudo tail -f /var/log/karyaradhane.err.log
sudo service nginx status
sudo service postgresql status
```

| Problem | Fix |
|---------|-----|
| Desktop can't connect | Check GCP firewall allows HTTP; verify `curl http://IP/health` from your PC |
| 502 from nginx | `sudo supervisorctl restart karyaradhane` |
| DB errors | Check `/opt/karyaradhane/backend/.env` DATABASE_URL and PostgreSQL password |

---

## Cost

~**$25–30/month** for e2-medium + 20 GB disk.

---

## Security (production)

1. Change default passwords in `.env` and PostgreSQL
2. Set a strong `SECRET_KEY`
3. Add a domain + Let's Encrypt SSL (see `deployment/nginx.conf` HTTPS section)
4. Never commit `backend/.env` to git

---

## Email notifications (assignee alerts)

The desktop app uses the **server** API. Email is sent from the VM's `/opt/karyaradhane/backend/.env`, not your Windows `backend/.env`.

1. On the VM, edit `.env`:

```bash
sudo ee /opt/karyaradhane/backend/.env
```

2. Set (Gmail example — use an [App Password](https://myaccount.google.com/apppasswords), not your normal password):

```env
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM=your@gmail.com
SMTP_USE_TLS=true

IMAP_HOST=imap.gmail.com
IMAP_PORT=993
IMAP_USER=your@gmail.com
IMAP_PASSWORD=your-16-char-app-password
IMAP_USE_SSL=true
```

3. Restart the API and verify:

```bash
sudo supervisorctl -c /usr/local/etc/supervisord.conf restart karyaradhane
curl http://127.0.0.1/health
```

Expect `"email_enabled":true`.

4. **Assignee must have a real email** — sample users use `user@example.com` / `admin@example.com` (not deliverable). Assign by typing the person's real Gmail/work address, or update the user record in the app.

5. **Re-assign the task** after enabling email (earlier assignments were skipped while email was off).

6. Check logs if mail still fails:

```bash
sudo tail -50 /var/log/karyaradhane.out.log
sudo tail -50 /var/log/karyaradhane.err.log
```
