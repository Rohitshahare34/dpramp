#!/bin/bash
# Complete AWS Deployment Fix for DPRAMP Static Files

echo "🚀 DPRAMP AWS Deployment Fix Script"
echo "====================================="

# Navigate to project directory
cd /var/www/dpramp

# Stop services first
echo "🛑 Stopping services..."
sudo systemctl stop nginx
sudo systemctl stop gunicorn

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found!"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Load database backup (only if needed)
if [ ! -f "db_loaded.flag" ]; then
    echo "📊 Loading database backup..."
    python manage.py loaddata database_backup.json
    touch db_loaded.flag
fi

# Clear and collect static files
echo "🎨 Clearing and collecting static files..."
rm -rf staticfiles/
python manage.py collectstatic --clear --noinput

# Set proper permissions
echo "🔐 Setting proper permissions..."
sudo chown -R www-data:www-data /var/www/dpramp/
sudo chmod -R 755 /var/www/dpramp/staticfiles/
sudo chmod -R 755 /var/www/dpramp/media/

# Check if static files exist
echo "🔍 Verifying static files..."
if [ -f "staticfiles/img/logo.png" ]; then
    echo "✅ Logo file exists"
else
    echo "❌ Logo file missing!"
fi

if [ -f "staticfiles/css/style.css" ]; then
    echo "✅ CSS file exists"
else
    echo "❌ CSS file missing!"
fi

if [ -d "staticfiles/img/rough_imgs" ]; then
    echo "✅ Rough images folder exists"
    echo "📁 Files in rough_imgs: $(ls -1 staticfiles/img/rough_imgs | wc -l)"
else
    echo "❌ Rough images folder missing!"
fi

# Test Django settings
echo "⚙️ Testing Django configuration..."
python manage.py check --deploy

# Restart services
echo "🔄 Restarting services..."
sudo systemctl start gunicorn
sudo systemctl start nginx

# Check service status
echo "🔍 Checking service status..."
sudo systemctl status gunicorn --no-pager -l
sudo systemctl status nginx --no-pager -l

# Test URLs
echo "🌐 Testing URLs..."
curl -I http://localhost:8000/static/css/style.css
curl -I http://localhost:8000/static/img/logo.png
curl -I http://localhost:8000/static/logos/logo.png

echo "✅ Deployment completed!"
echo "🌐 Your site should be live at: https://dpramp.com"
echo ""
echo "🔍 If images still don't show, check:"
echo "1. NGINX configuration: /etc/nginx/sites-available/dpramp"
echo "2. Django logs: /var/log/nginx/error.log"
echo "3. Gunicorn logs: journalctl -u gunicorn"
