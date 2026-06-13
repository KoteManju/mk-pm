# Deploy mk-pm to FreeBSD on Google Cloud

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
     - Version: **freebsd-13-2** (or latest 13.x)
     - Size: **20 GB**
   - **Firewall:** check **Allow HTTP traffic** and **Allow HTTPS traffic**
4. Click **Create**
5. Copy the **External IP** (e.g. `34.xxx.xxx.xxx`)

### Optional: install gcloud on Windows

Download: https://cloud.google.com/sdk/docs/install

Then create the VM from PowerShell:

```powershell
gcloud config set project YOUR_PROJECT_ID
gcloud compute instances create mk-pm-server `
  --image-family=freebsd-13-2 `
  --image-project=freebsd-org-cloud-dev `
  --machine-type=e2-medium `
  --boot-disk-size=20GB `
  --zone=us-central1-a `
  --tags=http-server,https-server
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
