# Production deploy (AWS Ubuntu) — dpramp.com

## One command (copy-paste on server)

```bash
cd /var/www/dpramp && \
source venv/bin/activate && \
git fetch origin && \
git reset --hard origin/main && \
pip install -r requirements.txt && \
python manage.py migrate && \
python manage.py fix_missing_media && \
python manage.py collectstatic --noinput && \
pkill -f "gunicorn.*dpramp_project" 2>/dev/null || true && \
sleep 2 && \
nohup gunicorn --workers 3 --bind 127.0.0.1:8000 dpramp_project.wsgi:application >> gunicorn.log 2>&1 & \
sleep 1 && \
sudo systemctl reload nginx && \
git log --oneline -1 && \
echo "=== Deploy finished ==="
```

**Note:** `git reset --hard` removes local edits on the server (e.g. manual `settings.py` changes). Keep production secrets in a file outside Git or re-apply after deploy.

If `git pull` fails with “local changes”, use `git reset --hard origin/main` instead of `git pull`.

---

# Production deploy fixes (dpramp.com)

## 1. Image 404 (`Drone_Maintenance.jpg`, `ChatGPT_Image_Apr_18...`)

Media files are **not in Git**. Database paths point to `/media/...` but files must exist on the server.

On the server after `git pull`:

```bash
cd /var/www/dpramp
source venv/bin/activate   # if you use a venv
python manage.py migrate
python manage.py fix_missing_media
python manage.py collectstatic --noinput
```

Ensure Nginx serves media (example):

```nginx
location /media/ {
    alias /var/www/dpramp/media/;
}
```

Check files exist:

```bash
ls -la /var/www/dpramp/media/drones/Drone_Maintenance.jpg
ls -la /var/www/dpramp/media/projects/ChatGPT_Image_Apr_18_2026_01_53_56_PM.png
```

If still missing, copy from your PC:

```bash
scp -r "media/drones" "media/projects" "media/thumbnails" user@server:/var/www/dpramp/media/
```

---

## 2. Counselling form 403 (`/engineering-counselling/register/`)

Most common cause on HTTPS: **`CSRF_TRUSTED_ORIGINS`** not set (fixed in `settings.py`).

After pull, restart app:

```bash
sudo systemctl restart gunicorn
# or your service name
sudo systemctl reload nginx
```

Debug logs:

```bash
tail -100 /var/www/dpramp/gunicorn.log
sudo tail -100 /var/log/nginx/error.log
python manage.py showmigrations notes
```

Test POST (replace CSRF from browser devtools):

```bash
curl -i -X POST https://dpramp.com/engineering-counselling/register/ \
  -H "Referer: https://dpramp.com/" \
  -H "X-CSRFToken: YOUR_TOKEN" \
  -b "csrftoken=YOUR_TOKEN"
```

---

## 3. Checklist after each deploy

```bash
git pull origin main
python manage.py migrate
python manage.py fix_missing_media
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```
