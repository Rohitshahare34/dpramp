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
