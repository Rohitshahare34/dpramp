#!/bin/bash
# Deployment script for DPRAMP static files

echo "🚀 DPRAMP Static Files Deployment Script"
echo "=========================================="

# Navigate to project directory
cd /var/www/dpramp

# Activate virtual environment (if exists)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Step 1: Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Step 2: Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Step 3: Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Step 4: Load database backup (only if needed)
if [ ! -f "db_loaded.flag" ]; then
    echo "📊 Loading database backup..."
    python manage.py loaddata database_backup.json
    touch db_loaded.flag
fi

# Step 5: Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# Step 6: Set permissions
echo "🔐 Setting permissions..."
chown -R www-data:www-data /var/www/dpramp/
chmod -R 755 /var/www/dpramp/staticfiles/

# Step 7: Restart Gunicorn
echo "🔄 Restarting Gunicorn..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "✅ Deployment completed successfully!"
echo "🌐 Your site should be live at: https://dpramp.com"
