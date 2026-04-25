#!/bin/bash
# Fix missing static files on AWS server

echo "🔧 Fixing missing static files..."

cd /var/www/dpramp

# Create missing files
cp "staticfiles/img/rough imgs/contact-logo.png" "staticfiles/img/logo.png"
cp "staticfiles/img/bg.png" "staticfiles/img/overlay.png"

# Set permissions
sudo chown -R www-data:www-data staticfiles/
sudo chmod -R 755 staticfiles/

echo "✅ Missing static files fixed!"
echo "🔄 Restarting services..."

sudo systemctl restart nginx
sudo systemctl restart gunicorn

echo "🎉 All done! Site should be working now."
